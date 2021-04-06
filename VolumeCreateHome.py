#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def send(*bargs):
 cmdline=['/TopStor/queuethis.sh','VolumeCreateHome.py','running',bargs[-1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
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
   cmdline=['/TopStor/queuethis.sh','VolumeCreateHome.py','canceled',bargs[-1]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   return 3
 z=['/TopStor/pump.sh','VolumeCreateHome']
 for arg in args[:-2]:
  z.append(arg)
 msg={'req': 'VolumeCreate', 'reply':z}
 with open('/root/VolumeCreate','a') as f:
  f.write('myhost='+ownerip[0][1]+' '+myhost+' '+str(z)+'\n')
 sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
 cmdline=['/TopStor/queuethis.sh','VolumeCreateHome.py','stop',bargs[-1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 return

if __name__=='__main__':
 send(*sys.argv[1:])
