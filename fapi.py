#!/bin/python3.6
import flask, os, Evacuate
from flask import request, jsonify
import Hostsconfig
from Hostconfig import config
from allphysicalinfo import getall 
import sqlite3
from etcdget2 import etcdgetjson
from etcdgetpy import etcdget  as get
from sendhost import sendhost
from socket import gethostname as hostname
from getlogs import getlogs
from fapistats import allvolstats, levelthis
from datetime import datetime


os.environ['ETCDCTL_API'] = '3'
alldsks = []
allpools = 0
allgroups = []
allvolumes = []
allusers = []
readyhosts = []
activehosts = []
losthosts = []
possiblehosts = []
pooldict = dict()
app = flask.Flask(__name__)
app.config["DEBUG"] = True
logcatalog = ''
with open('/var/www/html/des20/msgsglobal.txt') as f:
 logcatalog = f.read().split('\n')
logdict = dict()
for log in logcatalog:
 msgcode= log.split(':')[0]
 logdict[msgcode] = log.replace(msgcode+':','').split(' ')
myhost = hostname()

def postchange(cmndstring,host='leader'):
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 ownerip=get(host,'--prefix')
 sendhost(ownerip[0][1], str(msg),'recvreply',myhost)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def getusers():
 userlst = etcdgetjson('usersinfo','--prefix') 
 uid = 0
 users = []
 for user in userlst:
  username = user['name'].replace('usersinfo/','')
  users.append([username,str(uid)]) 
  uid += 1
 return users

def getgroups():
 groupslst = etcdgetjson('usersigroup','--prefix') 
 gid = 0
 groups = []
 for group in groupslst:
  grpusers = group['prop'].split('/')[2]
  groupname = group['name'].replace('usersigroup/','')
  groups.append([groupname,str(gid), grpusers]) 
  gid += 1
 return groups

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''

def getpools():
 global pooldict
 pools = get('pools/','--prefix')
 poolinfo = []
 pid = 0
 for pool in pools:
  poolinfo.append({'id':pid, 'owner': pool[1], 'text':pool[0].split('/')[1]})
  pid += 1
  pooldict[pool[0].split('/')[1]] = {'id': pid, 'owner': pool[1] }
 return poolinfo
 
@app.route('/api/v1/hosts/info', methods=['GET','POST'])
def hostsinfo():
 global allhosts, readyhosts, activehosts, losthosts, possiblehosts
 allhosts = Hostsconfig.getall()
 return jsonify(allhosts)

@app.route('/api/v1/hosts/allinfo', methods=['GET','POST'])
def hostsallinfo():
 global allhosts, readyhosts, activehosts, losthosts, possiblehosts
 hostsinfo()
 hostslost()  
 hostspossible()
 return jsonify({'all': allhosts, 'active': activehosts, 'ready':readyhosts, 'possible':possiblehosts, 'lost':losthosts})


@app.route('/api/v1/hosts/ready', methods=['GET','POST'])
def hostsready():
 global allhosts, readyhosts, activehosts, losthosts, possiblehosts
 hosts = get('ready','--prefix')
 readyhosts = []
 hid = 0
 for host in hosts:
  name = host[0].replace('ready/','')
  ip = host[1]
  readyhosts.append({'name':name, 'ip': ip, 'id': hid}) 
  hid +=1
 return jsonify(readyhosts)

@app.route('/api/v1/hosts/active', methods=['GET','POST'])
def hostsactive():
 global allhosts, readyhosts, activehosts, losthosts, possiblehosts
 hosts = get('ActivePartners','--prefix')
 activehosts = []
 hid = 0
 for host in hosts:
  name = host[0].replace('ActivePartners/','')
  ip = host[1]
  activehosts.append({'name':name, 'ip': ip, 'id': hid}) 
  hid +=1
 return jsonify(activehosts)

@app.route('/api/v1/hosts/possible', methods=['GET','POST'])
def hostspossible():
 global allhosts, readyhosts, activehosts, losthosts, possiblehosts
 hosts = get('possible','--prefix')
 possiblehosts = []
 hid = 0
 for host in hosts:
  name = host[0].replace('possible','')
  ip = host[1]
  possiblehosts.append({'name':name, 'ip': ip, 'id': hid}) 
  hid +=1
 return jsonify(possiblehosts)

@app.route('/api/v1/hosts/lost', methods=['GET','POST'])
def hostslost():
 global allhosts, readyhosts, activehosts, losthosts, possiblehosts
 hostsready()
 hostsactive()
 losthosts = []
 hid = 0
 for active in activehosts:
  if active['name'] not in str(readyhosts): 
   losthosts.append({'id': hid, 'name': active['name'], 'ip': active['ip']})
   hid += 1
 return jsonify(losthosts)

@app.route('/api/v1/pools/dgsinfo', methods=['GET','POST'])
def dgsinfo():
 global allinfo 
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 dgsinfo = {'raids':allinfo['raids'], 'pools':allinfo['pools'], 'disks':allinfo['disks']}
 return jsonify(dgsinfo)


@app.route('/api/v1/volumes/stats', methods=['GET','POST'])
def volumestats():
 global allinfo 
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 volstats = allvolstats(allinfo)
 return jsonify(volstats)

@app.route('/api/v1/volumes/volumelist', methods=['GET','POST'])
def volumeslist():
 global allinfo 
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 volumes = []
 vid = 0
 for vol in allinfo['volumes']:
  volumes.append({'id':vid, 'text':vol.split('_')[0], 'fullname':vol,'pool':allinfo['volumes'][vol]['pool']})
  vid += 1
 return jsonify(volumes)



@app.route('/api/v1/volumes/poolsinfo', methods=['GET','POST'])
def volpoolsinfo():
 global allpools
 allpools = getpools()
 return jsonify({'results':allpools})

@app.route('/api/v1/volumes/snapshots/snapshotsinfo', methods=['GET','POST'])
def volumessnapshotsinfo():
 global allvolumes, alldsks, allinfo
 snaplist = {'Once':[], 'Minutely': [], 'Hourly': [], 'Weekly':[]}
 periodlist = {'Minutely': [], 'Hourly': [], 'Weekly':[]}
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 allgroups = getgroups()
 alllist = []
 snappriods = []
 for snap in allinfo['snapshots']:
  allinfo['snapshots'][snap]['date'] = datetime.strptime(allinfo['snapshots'][snap]['creation'], '%a %b %d %Y').strftime('%d-%B-%Y')
  snaplist[allinfo['snapshots'][snap]['snaptype']].append(allinfo['snapshots'][snap].copy())
  alllist.append(allinfo['snapshots'][snap].copy())
 for period in allinfo['snapperiods']:
  snappriods.append(allinfo['snapperiods'][period].copy())
  periodlist[allinfo['snapperiods'][period]['periodtype']].append(allinfo['snapperiods'][period].copy())
 return jsonify({'allsnaps':alllist, 'Once':snaplist['Once'], 'Hourly':snaplist['Hourly'], 'Weekly':snaplist['Weekly'], 'Minutely':snaplist['Minutely'] ,'allperiods':snappriods, 'Minutelyperiod':periodlist['Minutely'], 'Hourlyperiod':periodlist['Hourly'], 'Weeklyperiod':periodlist['Weekly']})

def volumesinfo(prot='all'):
 global allvolumes, alldsks, allinfo
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 allgroups = getgroups()
 volumes = []
 if prot == 'all':
   prot = 'S'
   prot2 = 'H'
 else:
  prot2 = prot
 for volume in allinfo['volumes']:
  if prot in allinfo['volumes'][volume]['prot'] or prot2 in allinfo['volumes'][volume]['prot']:
   volgrps = []
   for group in allgroups:
    try:
     if group[0] in allinfo['volumes'][volume]['groups'].split(','):
      volgrps.append(group[1])
    except:
      print(allinfo['volumes'][volume])
      print('###########################################################')
   allinfo['volumes'][volume]['groups'] = volgrps
   volumes.append(allinfo['volumes'][volume])
 return volumes

@app.route('/api/v1/volumes/CIFS/volumesinfo', methods=['GET','POST'])
def volumescifsinfo():
 volumes = volumesinfo('CIFS') 
 return jsonify({'allvolumes':volumes})

@app.route('/api/v1/volumes/NFS/volumesinfo', methods=['GET','POST'])
def volumesnfsinfo():
 volumes = volumesinfo('NFS') 
 return jsonify({'allvolumes':volumes})

@app.route('/api/v1/volumes/HOME/volumesinfo', methods=['GET','POST'])
def volumeshomeinfo():
 volumes = volumesinfo('HOME') 
 return jsonify({'allvolumes':volumes})

@app.route('/api/v1/volumes/volumesinfo', methods=['GET','POST'])
def volumesallinfo():
 volumes = volumesinfo() 
 return jsonify({'allvolumes':volumes})



@app.route('/api/v1/pools/poolsinfo', methods=['GET','POST'])
def poolsinfo():
 global allpools
 allpools = getpools()
 allpools.append({'id':len(allpools), 'text':'-------'})
 return jsonify({'results':allpools})

@app.route('/api/v1/groups/groupchange', methods=['GET','POST'])
def groupchange():
 data = request.args.to_dict()
 usrs = data.get('users')
 usrstr = ''
 if len(usrs) < 1:
  usrstr = 'NoUser'
 else:
  for usr in usrs.split(','):
   for suser in allusers:
    if str(suser['id']) == str(usr):
     usrstr += suser['name']+',' 
  usrstr = usrstr[:-1]
 cmndstring = '/TopStor/pump.sh UnixChangeGroup '+data.get('name')+' users'+usrstr+' admin'
 postchange(cmndstring)
 return data


@app.route('/api/v1/users/userchange', methods=['GET','POST'])
def userchange():
 data = request.args.to_dict()
 grps = data.get('groups')
 groupstr = ''
 allgroups = getgroups()
 if len(grps) < 1:
  groupstr = 'NoGroup'
 else:
  for grp in grps.split(','):
   groupstr += allgroups[int(grp)][0]+','
  groupstr = groupstr[:-1]
 cmndstring = '/TopStor/pump.sh UnixChangeUser '+data.get('name')+' groups'+groupstr+' admin'
 postchange(cmndstring)
 return data

@app.route('/api/v1/info/logs', methods=['GET','POST'])
def getalllogs():
 notif = getlogs()
 return jsonify({'alllogs': notif})


@app.route('/api/v1/info/notification', methods=['GET','POST'])
def getnotification():
 notifbody = get('notification')[0].split(' ')[1:]
 msg = logdict[notifbody[3]]
 msgbody = '.'
 notifc = 6
 for word in msg[4:]:
  if word == ':':
   try:
    msgbody = msgbody[:-1]+' '+notifbody[notifc]+'.'
   except:
    msgbody = msgbody +' '+notifbody+'parseerror.'
   notifc += 1
  elif len(word) > 0:
   msgbody = msgbody[:-1]+' '+word+'.' 
 notif = { 'importance':msg[0].replace(':',''), 'msgcode': notifbody[3], 'date':notifbody[0], 'time':notifbody[1],
	 'host':notifbody[2], 'type':notifbody[4], 'user': notifbody[5], 'msgbody': msgbody[1:]} 
 return jsonify(notif)

@app.route('/api/v1/volumes/snapshots/create', methods=['GET','POST'])
def volumesnapshotscreate():
 data = request.args.to_dict()
 datastr = ''
 data['user'] = 'admin'
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 ownerip = allinfo['hosts'][data['owner']]['ipaddress']
 switch = { 'Once':['snapsel','name','pool','volume'], 'Minutely':['snapsel', 'pool', 'volume', 'every', 'keep'],
	'Hourly':['snapsel', 'pool', 'volume', 'sminute', 'every', 'keep'], 
	'Weekly':['snapsel', 'pool', 'volume', 'stime', 'every', 'keep'] }
 datastr = ''
 for param in switch[data['snapsel']]:
  datastr +=data[param]+' '
 #datastr = data['name']+' '+data['pool']+' '+data['volume']+' '+data['user']
 print('#############################')
 print(data)
 print(datastr)
 print('###########################')
 cmndstring = '/TopStor/pump.sh SnapshotCreate'+datastr+' '+data['user']
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 sendhost(ownerip, str(msg),'recvreply',myhost)
 return data





@app.route('/api/v1/volumes/create', methods=['GET','POST'])
def volumecreate():
 data = request.args.to_dict()
 datastr = ''
 data['user'] = 'admin'
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 ownerip = allinfo['hosts'][allinfo['pools'][data['pool']]['host']]['ipaddress']
 datastr = data['pool']+' '+data['name']+' '+data['size']+' '+data['groups']+' '+data['ipaddress']+' '+data['Subnet']+' '+data['user']+' '+data['owner']+' '+data['user']
 print('#############################')
 print(data)
 print(datastr)
 print('###########################')
 cmndstring = '/TopStor/pump.sh VolumeCreate'+data['type']+' '+datastr
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 sendhost(ownerip, str(msg),'recvreply',myhost)
 return data

@app.route('/api/v1/volumes/config', methods=['GET','POST'])
def volumeconfig():
 global allinfo
 data = request.args.to_dict()
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 volume = allinfo['volumes'][data['volume']]
 owner = volume['host']
 ownerip = allinfo['hosts'][owner]['ipaddress']
 datastr = ''
 if 'groups' in data and len(data['groups']) < 1: 
  data['groups'] = 'NoGroup'
 data['user'] = 'admin'
 for ele in data:
  volume[ele] = data[ele] 
 datastr = volume['pool']+' '+volume['name']+' '+volume['quota']+' '+volume['groups']+' '+volume['ipaddress']+' '+volume['Subnet']+' '+volume['host']+' '+volume['user']
 print('#############################')
 print(data)
 print(datastr)
 print('###########################')
 cmndstring = '/TopStor/pump.sh VolumeChange'+data['type']+' '+datastr
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 sendhost(ownerip, str(msg),'recvreply',myhost)
 #config(data)
 return data



@app.route('/api/v1/hosts/config', methods=['GET','POST'])
def hostconfig():
 data = request.args.to_dict()
 datastr = ''
 data['user'] = 'admin'
 for ele in data:
  datastr += ele+'='+data[ele]+' '
 datastr = datastr[:-1]
 #cmndstring = '/TopStor/pump.sh Hostconfig.py '+datastr+' user=admin'
 #postchange(cmndstring,'ready/'+data['name'])
 print('#############################')
 print(data)
 print('###########################')
 config(data)
 return data

@app.route('/api/v1/hosts/evacuate', methods=['GET','POST'])
def hostevacuate():
 data = request.args.to_dict()
 args = data['name']+' '+data['Myname'] 
 Evacuate.do(data['name'],'admin') 
 return data

@app.route('/api/v1/volumes/snapshots/snaprollback', methods=['GET','POST'])
def volumesnapshotrol():
 global allinfo 
 data = request.args.to_dict()
 data['user'] = 'admin'
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 volume = allinfo['snapshots'][data['name']]['volume']
 pool = allinfo['snapshots'][data['name']]['pool']
 owner = allinfo['snapshots'][data['name']]['host']
 ownerip = allinfo['hosts'][owner]['ipaddress']
 cmndstring = "/TopStor/pump.sh SnapShotRollback "+pool+" "+volume+" "+data['name']+" "+data['user']
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 print('##################################')
 print(data)
 print('################################333')
 sendhost(ownerip, str(msg),'recvreply',myhost)
        		 
 return data


@app.route('/api/v1/volumes/snapshots/perioddelete', methods=['GET','POST'])
def volumesnapshotperioddel():
 data = request.args.to_dict()
 data['user'] = 'admin'
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 owner = allinfo['snapperiods'][data['name']]['host']
 ownerip = allinfo['hosts'][owner]['ipaddress']
 cmndstring = "/TopStor/pump.sh SnapShotPeriodDelete "+data['name']+" "+data['user']
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 sendhost(ownerip, str(msg),'recvreply',myhost)
 return data  


@app.route('/api/v1/volumes/snapshots/snapshotdel', methods=['GET','POST'])
def volumesnapshotdel():
 global allinfo 
 data = request.args.to_dict()
 data['user'] = 'admin'
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 volume = allinfo['snapshots'][data['name']]['volume']
 pool = allinfo['snapshots'][data['name']]['pool']
 owner = allinfo['snapshots'][data['name']]['host']
 ownerip = allinfo['hosts'][owner]['ipaddress']
 cmndstring = "/TopStor/pump.sh SnapShotDelete "+pool+" "+volume+" "+data['name']+" "+data['user']
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 print('##################################')
 print(data)
 print('################################333')
 sendhost(ownerip, str(msg),'recvreply',myhost)
        		 
 return data




@app.route('/api/v1/volumes/volumedel', methods=['GET','POST'])
def volumedel():
 global allinfo 
 data = request.args.to_dict()
 data['user'] = 'admin'
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 pool = allinfo['volumes'][data['name']]['pool']
 owner = allinfo['volumes'][data['name']]['host']
 ownerip = allinfo['hosts'][owner]['ipaddress']
 cmndstring = "/TopStor/pump.sh VolumeDelete"+data['type']+" "+pool+" "+data['name']+" "+data['type']+" "+data['user']
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 print('##################################')
 print(data)
 print('################################333')
 sendhost(ownerip, str(msg),'recvreply',myhost)
        		 
 return data

@app.route('/api/v1/groups/groupdel', methods=['GET','POST'])
def groupdel():
 data = request.args.to_dict()
 cmndstring = '/TopStor/pump.sh UnixDelGroup '+data.get('name')+' admin'
 postchange(cmndstring)
 return data

@app.route('/api/v1/users/userdel', methods=['GET','POST'])
def userdel():
 data = request.args.to_dict()
 cmndstring = '/TopStor/pump.sh UnixDelUser '+data.get('name')+' admin'
 postchange(cmndstring)
 return data

@app.route('/api/v1/groups/UnixAddgroup', methods=['GET','POST'])
def UnixAddGroup():
 global allusers, allgroups
 data = request.args.to_dict()
 usrstr = ''
 usrs = data.get('users')
 if len(usrs) < 1:
  usrstr = 'NoUser'
 else:
  for usr in usrs.split(','):
   for suser in allusers:
    if str(suser['id']) == str(usr):
     usrstr += suser['name']+',' 
  usrstr = usrstr[:-1]
 cmndstring = '/TopStor/pump.sh UnixAddGroup '+data.get('name')+' '+' users'+usrstr+'  admin'
 postchange(cmndstring)
 return data
 

@app.route('/api/v1/users/UnixAddUser', methods=['GET','POST'])
def UnixAddUser():
 global allgroups
 data = request.args.to_dict()
 if 'NoHome' in data['Volpool']:
  pool = 'NoHome'
 else:
  pool = allpools[int(data.get('Volpool'))]['text']
 if '--' in pool:
  pool = 'NoHome'
 grps = data.get('groups')
 groupstr = ''
 allgroups = getgroups()
 if len(grps) < 1:
  groupstr = 'NoGroup'
 else:
  for grp in grps.split(','):
   groupstr += allgroups[int(grp)][0]+','
  groupstr = groupstr[:-1]
 cmndstring = '/TopStor/pump.sh UnixAddUser '+data.get('name')+' '+pool+' groups'+groupstr+' ' \
     +data.get('Password')+' '+data.get('Volsize')+'G '+data.get('HomeAddress')+' '+data.get('HomeSubnet')+' hoststub'+' admin'
 postchange(cmndstring)
 return data 

@app.route('/api/v1/volumes/grouplist', methods=['GET'])
def api_volumes_groupslist():
 global allgroups, allusers
 thegroup = [] 
 api_users_userslist()
 for group in allgroups:
  groupusers = []
  for user in allusers:
   if user['name'] in str(group[2]):
    groupusers.append(user['id'])
  if len(groupusers) < 1:
   groupusers=["NoUser"]
  thegroup.append({'text':group[0], 'id':group[1], 'users':groupusers})
 return jsonify({'results':thegroup})




@app.route('/api/v1/groups/grouplist', methods=['GET'])
def api_groups_groupslist():
 global allgroups, allusers
 thegroup = [] 
 api_users_userslist()
 for group in allgroups:
  if group[0] == 'Everyone':
   continue

  groupusers = []
  for user in allusers:
   if user['name'] in str(group[2]):
    groupusers.append(user['id'])
  if len(groupusers) < 1:
   groupusers=["NoUser"]
  thegroup.append({'name':group[0], 'id':group[1], 'users':groupusers})
 return jsonify({'allgroups':thegroup})

@app.route('/api/v1/users/userlist', methods=['GET'])
def api_users_userslist():
 global allgroups, allusers
 userlst = etcdgetjson('usersinfo','--prefix')
 allgroups = getgroups()
 userdict = dict()
 allusers = []
 for group in allgroups:
  groupid = group[1]
  grpusers = group[2].split(',')
  for grpuser in grpusers:
   if grpuser not in userdict:
    userdict[grpuser] = []
   userdict[grpuser].append(str(groupid))
 usersnohome = []
 nohomeid = 0
 uid = 0
 for user in userlst:
  username = user['name'].replace('usersinfo/','')
  usersize = user['prop'].split('/')[3]
  userpool = user['prop'].split('/')[1]
  if username not in userdict:
   groups = ['NoGroup']
  else:
   groups = userdict[username]
  allusers.append({"name":username, 'id':uid, "pool":userpool, "size":usersize, "groups":groups})
  uid += 1
  if 'NoHome' in userpool:
   usersnohome.append({ 'id':nohomeid, 'text': username })
   nohomeid += 1 
 alldict = dict()
 alldict['allusers'] = allusers
 alldict['allgroups'] = allgroups
 alldict['usersnohome'] = usersnohome
 return jsonify(alldict)

@app.route('/api/v1/groups/userlist', methods=['GET'])
def api_groups_userlist():
 global allusers
 usr = []
 api_users_userslist()
 for user in allusers:
  usr.append({'id':user['id'],'text':user['name']})
 return jsonify({'results':usr})


@app.route('/api/v1/users/grouplist', methods=['GET'])
def api_users_grouplist():
 global allgroups
 allgroups = getgroups()
 grp = []
 for group in allgroups:
  grp.append({'id':group[1],'text':group[0]})
 return jsonify({'results':grp})

@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_books = cur.execute('SELECT * FROM books;').fetchall()

    return jsonify(all_books)



@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/api/v1/resources/books', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * FROM books WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

app.run(host="0.0.0.0", port=5001)
