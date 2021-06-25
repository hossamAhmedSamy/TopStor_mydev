#!/bin/python3.6
from allphysicalinfo import getall 
import sys
from ast import literal_eval as mtuple
from etcdget2 import etcdgetjson
from etcdgetpy import etcdget  as get
from etcdput import etcdput  as put
from sendhost import sendhost
from socket import gethostname as hostname
from getlogs import getlogs
from fapistats import allvolstats, levelthis
from datetime import datetime
from getallraids import newraids, selectdisks
import logmsg

faultydisks = []
alltemplate = {'hosts':{}, 'pools':{ 'status', 'host'}, 'raids': {'status'},'disks':{'status'},  'volumes':{ 'groups', 'ipaddress', 'Subnet', 'quota'}}
parsetemplate = {'hosts':{'identity': { '__added__':('Sys01','the host :: is registered in the system'), '__removed__':('Sys02','the host :: is removed from the system')}}, 
                 'pools':{'identity':{'__added__':('Sys03',' the pool :: is registered in the system'), '__removed__': ('Sys04','the host :: is removed from the system')}, 'status':('Sys05',':: status is changed from :: to ::'), 'host': ('Sys06','the pool ownership is transferred from host :: to host ::.')},
                'raids':{'identity':{'__added__':('Sys07',' the raid :: is registered in the system'), '__removed__': ('Sys08','the raid :: is removed from the system')}, 'status':('Sys09',':: status is change from :: to ::')},
                'disks':{'identity':{'__added__':('Sys10',' the disk :: is registered in the system'), '__removed__': ('Sys11','the disk :: is removed from the system')}, 'status':('Sys12',':: status is change from :: to ::')},
                'volumes':{'identity':{'__added__':('Sys13',' the volume :: is registered in the system'), '__removed__': ('Sys14','the volume :: is removed from the system')},'groups':('Sys15', ' this volume ::  allowed groups are changed'), 'ipaddress':('Sys16',' the volume :: ipaddress is changed from :: to ::.'),  'Subnet':('Sys17', ' the volume :: ip subnet is changed from :: to ::.'), 'quota':('Sys18',' the volume :: maximum size is changed from :: to ::.')}
                }
allinfo = dict()
alllastinfo = dict()
changepot = dict() 
def parsechange():
 global changepot
 print('changepot',changepot)
 allmsgs = []
 parser = [] 
 for key in changepot:
  for element in changepot[key]:
   for change in changepot[key][element]:
    parser = [element]
    if isinstance(changepot[key][element][change],dict):
     for chng in changepot[key][element][change]:
      msgtext = parsetemplate[key][change][chng][1]
      msgcode = parsetemplate[key][change][chng][0]
      parser.append(changepot[key][element][change][chng])
    else:
     msgtext = parsetemplate[key][change][1]
     msgcode = parsetemplate[key][change][0]
     parser += list(changepot[key][element][change])
    fixedparser = parser.copy()
    parser.reverse()
    while '::' in msgtext:
     msgtext = msgtext.replace('::',parser.pop(),1)
    allmsgs.append((msgcode,*fixedparser))
 print(allmsgs)
 return allmsgs

def takedecision(allmsgs):
 global allinfo, faultydisks
 for msg in allmsgs:
  print('msg',*msg[1:])
  if any(x in msg[-1] for x in ['DEGRADED','FAULT','OFFLINE','__removed']):
   logmsg.sendlog(msg[0],'warning','system',*msg[1:])
  else:
   logmsg.sendlog(msg[0],'info','system',*msg[1:])
 faultydisks = get('disks','FAULT')
 for disk in allinfo['disks']:
  if disk in str(faultydisks):
   continue
  if all(x not in allinfo['disks'][disk]['status'] for x in ['ONLINE','free']):
   put('disks/FAULT/'+disk, allinfo['disks'][disk]['status'])
 return

def allcompare():
 global alllastinfo, allinfo, changepot
 last = alllastinfo.copy()
 current = allinfo.copy()
 for key in current:
  if key not in alltemplate:
    continue
  tocompare = alltemplate[key]
  for element in current[key]:
   if element not in last[key]:
    if key not in changepot:
     changepot[key] = dict()
    changepot[key][element] = {'identity':{'__added__':element}}
   else:
    for feature in tocompare:
     if last[key][element][feature] != current[key][element][feature]:
      if key not in changepot:
       changepot[key] = dict()
      if element not in changepot[key]:
       changepot[key][element] = dict() 
      changepot[key][element][feature] = (last[key][element][feature], current[key][element][feature])
    last[key].pop(element,None)
  if key not in changepot:
   last.pop(key)
 for key in last:
  if key not in alltemplate:
    continue
  for element in last[key]:
    if key not in changepot:
     changepot[key] = dict()
    changepot[key][element] = {'identity':{identity,'__removed__'}}
 return changepot 

def replacedisks():
 global allinfo, faultydisks
 for disk in faultydisks:
  diskname = disk[0].split('/')[2]
  raid = allinfo['disks'][diskname]['raid']
  raidinfo = allinfo['raids'][raid]
  print(raid)
  print(raidinfo)
 return

def checkhosts():
 global allinfo, alllastinfo
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 lastalldsks = get('host','last')
 if lastalldsks[0] == -1:
  put('hosts/last',str(allinfo) )
  return
 alllastinfo = mtuple(lastalldsks[0][1])
 allchange = allcompare() 
 allmsgs = parsechange()
 takedecision(allmsgs)
 put('hosts/last',str(allinfo))
 replacedisks()
 return allchange

def electspare(data):
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 keys = []
 dgsinfo = {'raids':allinfo['raids'], 'pools':allinfo['pools'], 'disks':allinfo['disks']}
 dgsinfo['newraid'] = newraids(allinfo['disks'])
 if data['useable'] not in dgsinfo['newraid'][data['redundancy']]:
  keys = list(dgsinfo['newraid'][data['redundancy']].keys())
  keys.append(float(data['useable']))
  keys.sort()
  diskindx = keys.index(float(data['useable'])) + 1
  if diskindx == len(keys):
   diskindx = len(keys) - 2 
  data['useable'] = keys[diskindx]
 disks =  dgsinfo['newraid'][data['redundancy']][data['useable']]
 if 'single' in data['redundancy']:
  selecteddisks= disks
 else:
  selecteddisks = selectdisks(disks,dgsinfo['newraid']['single'],allinfo['disks'])
 owner = allinfo['disks'][selecteddisks[0]]['host']
 ownerip = allinfo['hosts'][owner]['ipaddress']
 data['user'] = 'admin'
 diskstring = ''
 for dsk in selecteddisks:
  diskstring += dsk+":"+dsk[-5:]+" "
 if 'single' in data['redundancy']:
  datastr = 'Single '+data['user']+' '+owner+" "+selecteddisks[0]+" "+selecteddisks[0][-5:]+" nopool "+data['user']+" "+owner
 elif 'mirror' in data['redundancy']:
  datastr = 'mirror '+data['user']+' '+owner+" "+diskstring+"nopool "+data['user']+" "+owner
 elif 'volset' in data['redundancy']:
  datastr = 'stripeset '+data['user']+' '+owner+" "+diskstring+" "+data['user']+" "+owner
 elif 'raid5' in data['redundancy']:
  datastr = 'parity '+data['user']+' '+owner+" "+diskstring
 elif 'raid6plus' in data['redundancy']:
  datastr = 'parity3 '+data['user']+' '+owner+" "+diskstring+" "+data['user']+" "+owner
 elif 'raid6' in data['redundancy']:
  datastr = 'parity2 '+data['user']+' '+owner+" "+diskstring+" "+data['user']+" "+owner
 print('#############################3')
 print(selecteddisks)
 print('#########################333')
 cmndstring = '/TopStor/pump.sh DGsetPool '+datastr+' '+data['user']
 z= cmndstring.split(' ')
 msg={'req': 'Pumpthis', 'reply':z}
 #sendhost(ownerip, str(msg),'recvreply',myhost)
 
if __name__=='__main__':
 if len(sys.argv) > 1: 
  electspare(*sys.argv[1:])
 data = checkhosts()
 
