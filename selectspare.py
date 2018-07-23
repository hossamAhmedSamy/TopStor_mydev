#!/bin/python3.6
import subprocess,sys,socket
import json
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from etcdput import etcdput as put
import logmsg
disksvalue=[]

def mustattach(cmdline,disksvalue):
   print('################################################')
   print(len(disksvalue))
   print('disksvalue',disksvalue)
   if len(disksvalue) < 1 : 
    raise ValueError('no way cannot attach')
    return
   print('helskdlskdkddlsldssd#######################')
   cmd=cmdline
   spare=disksvalue[0][0]
   print(cmd,spare)
   disksvalue.pop(0)
   cmd.append(spare)
   print(cmd)
   try: 
    subprocess.check_call(cmd)
    return
   except subprocess.CalledProcessError:
    mustattach(cmdline[:-1],disksvalue) 
    print('selected disk',spare)
 
def norm(val):
 units={'B':1/1024**2,'K':1/1024, 'M': 1, 'G':1024 , 'T': 1024**2 }
 if val[-1] != 'B':
  return float(val) 
 else:
  if val[-2] in list(units.keys()):
   return float(val[:-2])*float(units[val[-2]])
  else:
   return float(val[:-1])*float(units['B'])
   
  
def selectspare(*args):
 myhost=socket.gethostname()
 faultdiskid='empty'
 faultdisk='empty'
 faultraid=spare=spareid='empty'
 faultraidall={}
 allop=get('hosts','--prefix')
 newop=get(args[0])
 newop=mtuple(newop[0])
 for newpool in newop:
  for newraid in newpool['raidlist']:
   if newraid['name'] != 'spares' and newraid['name'] != 'free':
    for newdisk in newraid['disklist']:
     if 'stripe' in newraid['name'] and 'empty' in faultdisk:
      runninghosts=[x['host'] for x in newraid['disklist'] ]
      faultdiskhost=newdisk['host']
      faultdiskpool=newpool['name']
      faultdisk=newdisk['name']
      faultdiskid=newdisk['id']
      faultraid=newraid['name']
      break;
     elif 'ONLI' not in newdisk['status'] and 'empty' in faultdisk:
      runninghosts=[x['host'] for x in newraid['disklist'] if x['name'] not in newdisk['name']]
      
      faultdiskhost=newdisk['host']
      faultdiskpool=newpool['name']
      faultdisk=newdisk['name']
      faultdiskid=newdisk['id']
      faultraid=newraid['name']
      break;
#   elif newraid['name'] == 'spares':
#    spare=newraid['disklist'][0]['name']
#    spareid=newraid['disklist'][0]['id']
 disksvalue=[]
 for hostpools in allop:
  pools=mtuple(hostpools[1])
  for newpool in pools:
   for newraid in newpool['raidlist']:
    if ('spare' in newraid['name'] or 'free' in newraid['name']) and len(newraid['disklist']) > 0: 
     mindisk=min(newraid['disklist'],key=lambda x:norm(x['size']))
     for newdisk in newraid['disklist']:
      diskvalue=0
      if newdisk['size'] == mindisk['size'] :
       diskvalue+=1
      elif norm(newdisk['size']) > norm(mindisk['size']): 
       diskvalue+=1-(norm(newdisk['size']) - norm(mindisk['size']))/norm(mindisk['size'])
      if 'spare' in newraid['name']:
       diskvalue+=10
      if newdisk['host'] not in runninghosts: 
       diskvalue+=100
      disksvalue.append((newdisk['name'],diskvalue)) 
   
 sparevalue=max(disksvalue,key=lambda x:x[1])
 disksvalue=sorted(disksvalue,key=lambda x:x[1], reverse=True)
 spare=disksvalue[0][0]   
 print('spares',spare,faultdisk,faultraid)
 if spare !='empty' and faultdisk !='empty'and 'logs' in faultraid :
  cmdline=['/sbin/zpool', 'remove', faultdiskpool,faultdisk]
  try:
   subprocess.check_call(cmdline)
   cmdline=['/sbin/zpool', 'remove', faultdiskpool,spare]
   subprocess.check_call(cmdline)
   cmdline=['/sbin/zpool', 'add', faultdiskpool,'log',spare]
   try: 
    subprocess.check_call(cmdline)
    logmsg.sendlog('Disu2','info','system', faultdiskid,spareid,myhost)
   except subprocess.CalledProcessError:
    logmsg.sendlog('Difa2','info','system', 'attach '+faultdiskid,spareid,myhost)
  except:
   pass 
 elif spare !='empty' and faultdisk !='empty'and 'cache' in faultraid :
  cmdline=['/sbin/zpool', 'remove', faultdiskpool,faultdisk]
  try:
   subprocess.check_call(cmdline)
   cmdline=['/sbin/zpool', 'remove', faultdiskpool,spare]
   subprocess.check_call(cmdline)
   cmdline=['/sbin/zpool', 'add', faultdiskpool,'cache',spare]
   try: 
    subprocess.check_call(cmdline)
    logmsg.sendlog('Disu2','info','system', faultdiskid,spareid,myhost)
   except subprocess.CalledProcessError:
    logmsg.sendlog('Difa2','info','system', 'attach '+faultdiskid,spareid,myhost)
  except:
       pass 
 elif spare !='empty' and faultdisk !='empty'and 'stripe' in faultraid:
  logmsg.sendlog('Dist2','info','system', faultdiskid,spareid,myhost)
  cmdline=['/sbin/zpool', 'attach','-f', faultdiskpool,faultdisk]
  print(cmdline,disksvalue)
  try: 
   mustattach(cmdline,disksvalue)
   logmsg.sendlog('Disu2','info','system', faultdiskid,spareid,myhost)
  except :
   logmsg.sendlog('Difa2','info','system', 'attach '+faultdiskid,spareid,myhost)
 elif spare !='empty' and faultdisk !='empty'and 'mirror' in faultraid:
  logmsg.sendlog('Dist2','info','system', faultdiskid,spareid,myhost)
  cmdline=['/sbin/zpool', 'detach', faultdiskpool,faultdisk]
  subprocess.check_call(cmdline)
 elif spare !='empty' and faultdisk !='empty':
  logmsg.sendlog('Dist2','info','system', faultdiskid,spareid,myhost)
  cmdline=['/sbin/zpool', 'replace', faultdiskpool,faultdisk]
  try:
   mustattach(cmdline,disksvalue)
   logmsg.sendlog('Disu2','info','system', faultdiskid,spareid,myhost)
  except subprocess.CalledProcessError:
   logmsg.sendlog('Difa2','info','system', 'attach '+faultdiskid,spareid,myhost)
 
if __name__=='__main__':
 selectspare(*sys.argv[1:])
