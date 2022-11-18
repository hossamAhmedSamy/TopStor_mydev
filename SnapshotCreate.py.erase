#!/usr/bin/python3
import sys, datetime
from logqueue import queuethis
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def send(*bargs):
 queuethis('SnapshotCreate.py','running',bargs[-1])
 if(len(bargs) < 3):
  args=bargs[0].split()
 else:
  args=bargs
 sel=args[0]
 pool=args[1]
 pool=str(pool)
 ownerlist=[]
 owner=""
 print('pool',pool)
 z=[]
 with open('/root/SnapshotCreate','w') as f:
  f.write('all='+str(args)+'\n')
 print('pool',pool)
 ownerlist=get('pools/'+pool)
 if len(ownerlist) == 1:
  print(ownerlist)
  owner=ownerlist[0]
 else:
  queuethis('SnapshotCreate.py','stop_canceled',bargs[-1])
  return 2
 with open('/root/SnapshotCreate','a') as f:
  f.write('owner='+owner+'\n')
 myhost=hostname()
 with open('/root/SnapshotCreate','a') as f:
  f.write('myhost='+myhost+'\n')
 ownerip=get('leader',owner)
 if ownerip[0]== -1:
  ownerip=get('known',owner)
  if ownerip[0]== -1:
   queuethis('SnapshotCreate.py','stop_canceled',bargs[-1])
   return 3
 z=['/TopStor/pump.sh','SnapshotCreate'+sel]
 for arg in args[1:]:
  z.append(arg)
 msg={'req': 'SnapshotCreate', 'reply':z}
 with open('/root/SnapshotCreate','a') as f:
  f.write('myhost='+ownerip[0][1]+' '+myhost+' '+str(z)+'\n')
 sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
 queuethis('SnapshotCreate.py','stop',bargs[-1])
 return 1

if __name__=='__main__':
 send(*sys.argv[1:])
