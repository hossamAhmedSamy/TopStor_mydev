#!/bin/python3.6
import flask
from flask import request, jsonify
import sqlite3
from etcdget2 import etcdgetjson
from etcdget import etcdget  as get
from sendhost import sendhost
from socket import gethostname as hostname
allpools = 0
allgroups = []
allusers = []
app = flask.Flask(__name__)
app.config["DEBUG"] = True
logcatalog = ''
with open('/var/www/html/des20/msgsglobal.txt') as f:
 logcatalog = f.read()
myhost = hostname()

def postchange(cmndstring):
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 ownerip=get('leader','--prefix')
 print(msg,myhost)
 sendhost(ownerip[0][1], str(msg),'recvreply',myhost)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

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
 pools = get('pools/','--prefix')
 poolinfo = []
 pid = 0
 for pool in pools:
  poolinfo.append({'id':pid, 'text':pool[0].split('/')[1]})
  pid += 1
 return poolinfo
 
@app.route('/api/v1/pools/poolsinfo', methods=['GET','xDelUserPOST'])
def poolsinfo():
 global allpools
 allpools = getpools()
 allpools.append({'id':len(allpools), 'text':'-------'})
 return jsonify({'results':allpools})

@app.route('/api/v1/users/userchange', methods=['GET','POST'])
def userchange():
 data = request.args.to_dict()
 print('data',data)
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


@app.route('/api/v1/info/notification', methods=['GET','POST'])
def getnotification():
 notif = get('notification')
 print(type(notif))
 return jsonify(notif)



@app.route('/api/v1/users/userdel', methods=['GET','POST'])
def userdel():
 data = request.args.to_dict()
 print('data',data)
 cmndstring = '/TopStor/pump.sh UnixDelUser '+data.get('name')+' admin'
 postchange(cmndstring)
 return data

@app.route('/api/v1/users/UnixAddUser', methods=['GET','POST'])
def UnixAddUser():
 global allgroups
 data = request.args.to_dict()
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
     +data.get('Password')+' '+data.get('Volsize')+'G '+data.get('HomeAddress')+' '+data.get('HomeSubnet')+' admin'
 postchange(cmndstring)
 return data 



@app.route('/api/v1/users/userlist', methods=['GET'])
def api_users_userslist():
 global allgroups
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
 users = []
 for user in userlst:
  username = user['name'].replace('usersinfo/','')
  usersize = user['prop'].split('/')[3]
  userpool = user['prop'].split('/')[1]
  if username not in userdict:
   groups = ['NoGroup']
  else:
   groups = userdict[username]
  allusers.append({"name":username, "pool":userpool, "size":usersize, "groups":groups})
 alldict = dict()
 alldict['allusers']=allusers
 alldict['allgroups']=allgroups
 return jsonify(alldict)


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
