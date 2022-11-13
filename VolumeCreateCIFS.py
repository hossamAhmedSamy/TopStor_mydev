#!/usr/bin/python3
import sys, datetime
from logqueue import queuethis
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def create(*bargs):
 queuethis('VolumeCreateCIFS.py','running',bargs[-1])
 if(len(bargs) < 3):
  args=bargs[0].split()
 else:
  args=bargs
 print(args)
 print(args[0])
 pool=args[0]
 pool=str(pool)
 z=[]
 with open('/root/VolumeCreate','w') as f:
  f.write('pool='+pool+'\n')
 owner=args[-2]
 with open('/root/VolumeCreate','a') as f:
  f.write('owner='+owner+'\n')
 myhost=hostname()
 with open('/root/VolumeCreate','a') as f:
  f.write('myhost='+myhost+'\n')
 ownerip=get('leader',owner)
 if ownerip[0]== -1:
  ownerip=get('known',owner)
  if ownerip[0]== -1:
   queuethis('VolumeCreateCIFS.py','stop_canceled',bargs[-1])
   return 3
 z=['/TopStor/pump.sh','VolumeCreateCIFS']
 for arg in args[:-2]:
  z.append(arg)
 msg={'req': 'VolumeCreate', 'reply':z}
 with open('/root/VolumeCreate','a') as f:
  f.write('myhost='+ownerip[0][1]+' '+myhost+' '+str(z)+'\n')
 sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
 queuethis('VolumeCreateCIFS.py','stop',bargs[-1])
 return

if __name__=='__main__':
 create(*sys.argv[1:])
