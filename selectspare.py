#!/bin/python3.6
import subprocess,sys,socket
import json
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from etcdput import etcdput as put
import logmsg

def selectspare(*args):
 myhost=socket.gethostname()
 faultdiskid='na'
 faultdisk='na'
 faultraid=spare=spareid='na'
 newop=get(args[0])
 newop=mtuple(newop[0])
 for newpool in newop:
  for newraid in newpool['raidlist']:
   if newraid['name'] != 'spares' and newraid['name'] != 'free':
    for newdisk in newraid['disklist']:
     if 'ONLI' not in newdisk['status']:
      faultdisk=newdisk['name']
      faultdiskid=newdisk['id']
      faultraid=newraid['name']
      break;
   elif newraid['name'] == 'spares':
    spare=newraid['disklist'][0]['name']
    spareid=newraid['disklist'][0]['id']
  if spare !='na' and faultdisk !='na'and ( 'cache' in faultraid or 'log' in faultraid ):
   cmdline=['/sbin/zpool', 'remove', newpool['name'],faultdisk]
  if spare !='na' and faultdisk !='na'and 'mirror' in faultraid:
   logmsg.sendlog('Dist2','info','system', faultdiskid,spareid,myhost)
   cmdline=['/sbin/zpool', 'replace', newpool['name'],faultdisk,spare]
   try:
    subprocess.check_call(cmdline)
    cmdline=['/sbin/zpool', 'detach', newpool['name'],faultdisk]
    try: 
     subprocess.check_call(cmdline)
     logmsg.sendlog('Disu2','info','system', faultdiskid,spareid,myhost)
    except subprocess.CalledProcessError:
     logmsg.sendlog('Difa2','info','system', 'attach'+faultdiskid,spareid,myhost)
   except:
        pass 

if __name__=='__main__':
 selectspare(*sys.argv[1:])
