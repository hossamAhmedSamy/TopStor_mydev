#!/bin/python3.6
import subprocess,sys,socket
import json
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from etcdput import etcdput as put
from etcddel import etcddel as dels 
import logmsg
disksvalue=[]

def delall(*args):
 if len(args) > 1:
  dels(args[1]+'/lists/'+args[0])
 else:
  dels('lists/'+args[0])

def getall(*args):
 if len(args) > 1:
  alls=get(args[1]+'/lists/'+args[0])
 else:
  alls=get('lists/'+args[0])
 if len(alls) > 0 and alls[0] != -1:
  alls=mtuple(alls[0])
  return alls
 else:
  return [-1]

def putall(*args):
 alls=getall(args[0])
 put(args[1]+'/lists/'+args[0],str(alls))

def mustattach(cmdline,disksallowed,defdisk,myhost):
   print('################################################')
   if len(disksallowed) < 1 : 
    raise ValueError('no way cannot attach')
    return 'na'
   print('helskdlskdkddlsldssd#######################')
   cmd=cmdline
   spare=disksallowed[0][0]
   if spare['pool']==defdisk['pool']:
    cmdline=['/sbin/zpool', 'remove', defdisk['pool'],spare['name']]
    subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmd.append(spare['name'])
   logmsg.sendlog('Dist2','info','system', defdisk['id'],spare['id'],myhost)
   try: 
    subprocess.check_call(cmd)
    logmsg.sendlog('Disu2','info','system', defdisk['id'],spare['id'],myhost)
    return spare['name'] 
   except subprocess.CalledProcessError:
    logmsg.sendlog('Difa2','info','system', defdisk['id'],spare['id'],myhost)
    disksallowed.pop(0)
    ret=mustattach(cmdline[:-1],disksallowed,defdisk,myhost) 
    return ret
 
def norm(val):
 units={'B':1/1024**2,'K':1/1024, 'M': 1, 'G':1024 , 'T': 1024**2 }
 if val[-1] != 'B':
  return float(val) 
 else:
  if val[-2] in list(units.keys()):
   return float(val[:-2])*float(units[val[-2]])
  else:
   return float(val[:-1])*float(units['B'])


def diskreplace(myhost,defdisks,hosts,alldisks,replacelist,raids,pools):
 if len(defdisks) < 1:
  print('no more defective disks checking for non-red host raids')
  if len(raids) < 1 :
   print('no raids too') 
   return
  raid=raids[0]
  raids.pop(0)
  myhostpools=[pool['name'] for pool in pools if pool['host']==myhost ]
  disksinraid=[(disk['name'],disk['host']) for disk in alldisks if disk['raid'] == raid['name'] and disk['pool'] == raid['pool'] and disk['pool'] in myhostpools]
  hcount=[]
  for host in hosts:
   hcount.append((host,str(disksinraid).count(host),raid['name']))
  print('print',hcount)
  diskreplace(myhost,defdisks,hosts,alldisks,replacelist,raids,pools)
  return

 defdisk=defdisks[0]
 disksinraid=[disk for disk in alldisks if disk['raid']==defdisk['raid'] and disk['name'] != defdisk['name'] and 'ONLI' in disk['changeop']]
 runninghosts=[disk['host'] for disk in alldisks if disk['raid']==defdisk['raid'] and disk['name'] != defdisk['name'] and 'ONLI' in disk['changeop']]
 mindisk=min(disksinraid,key=lambda x:norm(x['size']))
 disksvalues=[]
 for  rep in replacelist:
  diskvalue=0
  if rep['size'] == mindisk['size'] :
   diskvalue+=1
  elif norm(rep['size']) > norm(mindisk['size']): 
       diskvalue+=1-(norm(rep['size']) - norm(rep['size']))/norm(mindisk['size'])
  else:
   diskvalue=-100000
  if 'spare' in rep['raid']:
    diskvalue+=10
  if rep['host'] not in hosts: 
   diskvalue+=100
  disksvalues.append((rep,diskvalue)) 
 disksvalues=sorted(disksvalues,key=lambda x:x[1], reverse=True)
 if 'spare' in defdisk['raid'] :
  logmsg.sendlog('Dist3','info','system', defdisk['id'],defdisk['host'])
  cmdline=['/sbin/zpool', 'remove', defdisk['pool'],defdisk['name']]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  ret=replacelist
 elif 'logs' in defdisk['raid'] :
  cmdline=['/sbin/zpool', 'remove', defdisk['pool'],defdisk['name']]
  try:
   subprocess.check_call(cmdline)
   if spare['pool']==defdisk['pool']:
    cmdline=['/sbin/zpool', 'remove', defdisk['pool'],spare['name']]
    subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/sbin/zpool', 'add', faultdiskpool,'log']
   try: 
    ret=mustattach(cmdline,disksvalues,defdisk,myhost)
   except subprocess.CalledProcessError:
    pass
  except:
   pass 
 elif 'cache' in defdisk['raid'] :
  cmdline=['/sbin/zpool', 'remove', defdisk['pool'],defdisk['name']]
  try:
   subprocess.check_call(cmdline)
   cmdline=['/sbin/zpool', 'add', defdisk['pool'],'cache']
   try: 
    ret=mustattach(cmdline,disksvalues,defdisk,myhost)
   except subprocess.CalledProcessError:
    pass
  except:
   pass 
 elif 'stripe' in defdisk['raid'] :
  cmdline=['/sbin/zpool', 'attach','-f', defdisk['pool'],disks[0]['name']]
  try: 
   ret=mustattach(cmdline,disksvalues,defdisk,myhost)
  except :
    pass
 elif 'mirror' in defdisk['name']:
  cmdline=['/sbin/zpool', 'detach', defdisk['pool'],defdisk['name']]
  subprocess.run(cmdline,stdout=subprocess.PIPE)
  ret=replacelist
 else:
  cmdline=['/sbin/zpool', 'replace', defdisk['pool'],defdisk['name']]
  try:
   ret=mustattach(cmdline,disksvalues,defdisk,myhost)
  except subprocess.CalledProcessError:
   pass 
 replacelist=[x for x in replacelist if x['name']!=ret]
 defdisks=defdisks.pop(0)   
 diskreplace(myhost,defdisks,hosts,alldisks,replacelist,raids)
 
  
def selectspare(*args):
 myhost=args[0]
 print('hihi',myhost,)
 newop=getall(myhost)
 #allop=getall(myhost,'old')
 #diffop={k:newop[k] for k in allop if allop[k] != newop[k] and 'disk' in k}
 diskreplace(myhost,newop['defdisks'],newop['hosts'],newop['disks'],newop['freedisks']+newop['sparedisks'],newop['raids'],newop['pools'])
 return
 
 
if __name__=='__main__':
 selectspare(*sys.argv[1:])
