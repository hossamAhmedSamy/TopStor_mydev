#!/bin/python3.6
from allphysicalinfo import getall 
import sys
from etcdget2 import etcdgetjson
from etcdgetpy import etcdget  as get
from etcdput import etcdput  as put
from sendhost import sendhost
from socket import gethostname as hostname
from getlogs import getlogs
from fapistats import allvolstats, levelthis
from datetime import datetime
from getallraids import newraids, selectdisks
alltemplate = {'hosts':{}, 'pools':{ 'changeop', 'status', 'host'}, 'raids': {'changeop', 'status','host'},'disks':{'changeop' , 'status', 'raid', 'pool', 'id', 'host', 'size', 'devname'},  'volumes':{ 'groups', 'ipaddress', 'Subnet', 'host', 'quota'}}
allinfo = dict()
alllastinfo = dict()
changepot = dict() 
def allcompare(last,current):
 print(allinfo.keys())
 for key in current:
  if key not in alltemplate:
    continue
  tocompare = alltemplate[key]
  for identity in current[key]:
   if identity not in last[key]:
    if key not in changepot:
     changepot[key] = dict()
    changepot[key][identity] = ('None',identity)
   else:
    for comp in tocompare:
     if last[key][identity][comp] != current[key][identity][comp]:
      if key not in changepot:
       changepot[key] = dict()
      if identity not in changepot[key]:
       changepot[key][identity] = dict() 
      changepot[key][identity][comp] = (last[key][identity][comp], current[key][identity][comp])
    last[key].pop(identity,None)
  if key not in changepot:
   last.pop(key)
 for key in last:
  if key not in alltemplate:
    continue
  for identity in last[key]:
    if key not in changepot:
     changepot[key] = dict()
    changepot[key][identity] = (identity,'None')
 print(changepot)  
 return changepot 

def checkhosts():
 global allinfo, alllastinfo
 alldsks = get('host','current')
 lastalldsks = get('host','last')
 if lastalldsks[0] == -1:
  for hostinfo in alldsks:
   leftside = hostinfo[0].replace('current','last')
   put(leftside, hostinfo[1])
  return
 allinfo = getall(alldsks)
 alllastinfo = getall(lastalldsks)
 alllastinfo['pools']['inlast']= { 'name': 'inlast', 'status':'ONLINE' }
 allinfo['pools']['incurrent']= { 'name': 'incurrent','status':'ONLINE' }
 allinfo['pools']['inboth']= { 'name':'inboth','status': 'ONLINE' }
 alllastinfo['pools']['inboth']= { 'name':'inboth', 'status': 'DEGRADED' }
 allchange = allcompare(alllastinfo,allinfo) 
 print(allchange)
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
 
