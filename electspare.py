#!/bin/python3.6
from allphysicalinfo import getall 
import sys, subprocess, json
from ast import literal_eval as mtuple
from etcdget2 import etcdgetjson
from etcdgetpy import etcdget  as get
from etcddel import etcddel  as dels
from etcdput import etcdput  as put
from sendhost import sendhost
from socket import gethostname
from getlogs import getlogs
from fapistats import allvolstats, levelthis
from datetime import datetime
from getallraids import newraids, selectdisks, selectnewmirror
from copy import deepcopy 
import logmsg
myhost = ''
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
    fixedparser = deepcopy(parser)
    parser.reverse()
    while '::' in msgtext:
     msgtext = msgtext.replace('::',parser.pop(),1)
    allmsgs.append((msgcode,*fixedparser))
 return allmsgs

def mirrorattach(pool,cdisk,ndisk,raid):
 global myhost
 logmsg.sendlog('Dist6','info','system', ndisk,raid,pool,myhost)
 cmd = ['/sbin/zpool', 'attach', '-f', pool, cdisk, ndisk]
 print(pool,cdisk,ndisk)
 logmsg.sendlog('Dist2','info','system', cdisk, ndisk,myhost)
 cmdline3=['/sbin/zpool', 'labelclear', ndisk]
 subprocess.run(cmdline3,stdout=subprocess.PIPE)
 try: 
  subprocess.check_call(cmd)
  if 'attach' in cmd:
   logmsg.sendlog('Disu6','info','system', ndisk,raid,pool,myhost)
   put('fixpool/'+pool,'1')
  else:
   logmsg.sendlog('Disu2','info','system', cdisk, ndisk,myhost)
 except subprocess.CalledProcessError:
  print('attach problem')
  return 'fault'

def takedecision(allmsgs):
 global allinfo, faultydisks
 for msg in allmsgs:
  if any(x in msg[-1] for x in ['DEGRADED','FAULT','OFFLINE','__removed']):
   logmsg.sendlog(msg[0],'warning','system',*msg[1:])
  else:
   logmsg.sendlog(msg[0],'info','system',*msg[1:])
 faultydisks = get('disks','FAULT')
 if '-1' in str(faultydisks):
  faultydisks = [] 
 for disk in allinfo['disks']:
  if disk in str(faultydisks):
   continue
  #if all(x not in allinfo['disks'][disk]['status'] for x in ['ONLINE','free']):
  # put('disks/FAULT/'+disk, allinfo['disks'][disk]['status'])
 return

def allcompare():
 global alllastinfo, allinfo, changepot
 last = deepcopy(alllastinfo)
 current = deepcopy(allinfo)
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
     try:
      if last[key][element][feature] != current[key][element][feature]:
       if key not in changepot:
        changepot[key] = dict()
       if element not in changepot[key]:
        changepot[key][element] = dict() 
       changepot[key][element][feature] = (last[key][element][feature], current[key][element][feature])
     except:
      #dels('host','lasit')
      pass
    last[key].pop(element,None)
  if key not in changepot:
   last.pop(key)
 for key in last:
  if key not in alltemplate:
    continue
  for element in last[key]:
    if key not in changepot:
     changepot[key] = dict()
    changepot[key][element] = {'identity':{'__removed__':element}}
 return changepot 

def getoptimaldisk(fdisk,raidinfo):
 global myhost,allinfo
 if 'mirror' in raidinfo['name'] or 'stripe' in raidinfo['name']:
  newdisk = selectnewmirror(fdisk, allinfo['disks'], raidinfo)
  ndisk = allinfo['disks'][newdisk[0]]['name']
  pool = raidinfo['pool']
  raid = raidinfo['name'].split('_')[0]
  for disk in raidinfo['disks']:
   if disk != ndisk  and disk != fdisk:
    cdisk = disk
  print(pool,cdisk,ndisk,raid)
  mirrorattach(pool,cdisk,ndisk,raid)
 return


def replacedisks():
 global allinfo, faultydisks
 myhost=gethostname()
 availability = get('balance','--prefix')
 print(faultydisks)
 for disk in faultydisks:
  diskname = disk[0].split('/')[2]
  if diskname not in allinfo['disks']:
   #dels('disks/FAULT', diskname)
   continue
  raid = allinfo['disks'][diskname]['raid']
  raidinfo = allinfo['raids'][raid]
  if allinfo['raids'][raid]['host'] in myhost:
   getoptimaldisk(diskname,raidinfo)
 for raid in allinfo['raids']:
  if allinfo['raids'][raid]['status'] !='ONLINE' and allinfo['raids'][raid]['pool'] in str(availability):
   getoptimaldisk('NA',allinfo['raids'][raid])
 return

def checkhosts():
 global allinfo, alllastinfo
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 lastalldsks = get('hosts','last')
 if lastalldsks[0] == -1:
  put('hosts/last',json.dumps(allinfo) )
  return
 alllastinfo = mtuple(lastalldsks[0][1])
 allchange = allcompare() 
 if allchange:
  changec = int(get('hosts/change')[0])
  if changec not in [1,2,3,4,5]:
   changec = 0 
  if changec < 5:
   changec += 1
   put('hosts/change',str(changec))
   return
  put('hosts/change','0')
  with open('/root/electtmp','w') as f:
   f.write(str(alllastinfo))
   f.write('\n'+str(len(allinfo['hosts'])))
  print('found a change')
 allmsgs = parsechange()
 takedecision(allmsgs)
 put('hosts/last',json.dumps(allinfo))
 #replacedisks()
 return allchange

 
if __name__=='__main__':
 if len(sys.argv) > 1: 
  checkhosts(*sys.argv[1:])
 data = checkhosts()
 
