#!/bin/python3.6
import subprocess,sys
import json
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from etcdput import etcdput as put
import logmsg

def changeop(*args):
 newop=get(args[0])
 newop=mtuple(newop[0])
 if args[1] == 'dub':
  put('old'+args[0],str(newop))
  return
 oldop=get('old'+args[0])
 if oldop[0]==-1:
  print('noold')
  for newpool in newop:
   for newraid in newpool['raidlist']:
    for newdisk in newraid['disklist']:
     if 'ONLI' not in newdisk['status']:
      logmsg.sendlog('Diwa1','warning','system', newdisk['id'], newdisk['status'])
      cmdline='/sbin/zpool offline '+newpool['name']+' '+newdisk['name']
      subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  changeop(args[0],'dub')
  return
 oldop=mtuple(oldop[0])
 print('#######################################')
 changeop(args[0],'dub')
 for oldpool in oldop:
  for newpool in newop:
   if oldpool['name']==newpool['name']:
    if oldpool['status'] != newpool['status'] :
     if 'ONLI' in newpool['status']:
      logmsg.sendlog('Posu0','info','system', newpool['name'],newpool['status'])
     else:
      logmsg.sendlog('Powa1','warning','system', newpool['name'],newpool['status'])
    if oldpool['changeop'] != newpool['status']:
     for oldraid in oldpool['raidlist']:
      for newraid in newpool['raidlist']:
       if oldraid['name']==newraid['name']:
        if oldraid['status'] != newraid['status']:
         if 'ONLI' in newraid['status']:
          logmsg.sendlog('Rasu0','info','system', newraid['name'], newraid['status'])
         else:
          logmsg.sendlog('Rawa1','warning','system', newraid['name'], newraid['status'])
        if oldraid['changeop'] != newraid['status']:
         for oldisk in oldraid['disklist']:
          if oldisk['name'] not in str(newpool):
           logmsg.sendlog('Diwa4','warning','system', oldisk['id'], oldpool['name'])
           continue
          for newdisk in newraid['disklist']:
           if oldisk['name']==newdisk['name']:
            if oldisk['status'] != newdisk['status'] or oldisk['changeop'] != newdisk['status']: 
             if 'ONLI' in newdisk['status']:
              logmsg.sendlog('Disu0','info','system', newdisk['id'], newdisk['status'])
             else:
              logmsg.sendlog('Diwa1','warning','system', newdisk['id'], newdisk['status'])
              cmdline='/sbin/zpool offline '+newpool['name']+' '+newdisk['name']
              subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
            break  
        break
    break

            
 

if __name__=='__main__':
 changeop(*sys.argv[1:])
