#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def send(*bargs):
 if(len(bargs) < 3):
  args=bargs[0].split()
 else:
  args=bargs
 pool=args[0]
 pool=str(pool)
 ownerlist=[]
 owner=""
 z=[]
 with open('/root/SnapshotDelete','w') as f:
  f.write('all='+str(args)+'\n')
 print('pool',pool)
 ownerlist=get('pools/'+pool)
 if len(ownerlist) == 1:
  print(ownerlist)
  owner=ownerlist[0]
 else:
  exit()

 with open('/root/SnapshotDelete','a') as f:
  f.write('owner='+owner+'\n')
 myhost=hostname()
 with open('/root/SnapshotDelete','a') as f:
  f.write('myhost='+myhost+'\n')
 owneriplist=get('ready/'+owner)
 if str(owneriplist[0])!= '-1':
  ownerip=owneriplist[0]
 else:
   return 3
 z=['/TopStor/pump.sh','SnapShotDelete']
 for arg in args[:-1]:
  z.append(arg)
 msg={'req': 'SnapshotDelete', 'reply':z}
 with open('/root/SnapshotDelete','a') as f:
  f.write('myhost='+ownerip+' '+myhost+' '+str(z)+'\n')
 sendhost(ownerip, str(msg),'recvreply',myhost)
 return 1

if __name__=='__main__':
 send(*sys.argv[1:])
