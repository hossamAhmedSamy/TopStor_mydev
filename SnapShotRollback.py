#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def send(*bargs):
 cmdline=['/TopStor/queuethis.sh','SnapRollback.py','running',bargs[-1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 if(len(bargs) < 3):
  args=bargs[0].split()
 else:
  args=bargs
 pool=args[0]
 pool=str(pool)
 ownerlist=[]
 owner=""
 z=[]
 with open('/root/SnapshotRol','w') as f:
  f.write('all='+str(args)+'\n')
 print('pool',pool)
 ownerlist=get('pools/'+pool)
 print('ownerlist',ownerlist)
 if len(ownerlist) == 1:
  print(ownerlist)
  owner=ownerlist[0]
 else:
  exit()

 with open('/root/SnapshotRol','a') as f:
  f.write('owner='+owner+'\n')
 myhost=hostname()
 with open('/root/SnapshotRol','a') as f:
  f.write('myhost='+myhost+'\n')
 owneriplist=get('ready/'+owner)
 if str(owneriplist[0])!= '-1':
  ownerip=owneriplist[0]
  print('ownwerip',ownerip)
 else:
   return 3
 z=['/TopStor/pump.sh','SnapShotRollback']
 for arg in args:
  z.append(arg)
 msg={'req': 'SnapshotRollback', 'reply':z}
 with open('/root/SnapshotRol','a') as f:
  f.write('myhost='+ownerip+' '+myhost+' '+str(z)+'\n')
 sendhost(ownerip, str(msg),'recvreply',myhost)
 cmdline=['/TopStor/queuethis.sh','SnapRollback.py','stop',bargs[-1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 return 1

if __name__=='__main__':
 send(*sys.argv[1:])
