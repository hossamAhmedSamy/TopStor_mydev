#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def send(*args):
 print(args)
 print(args[0])
 pool=args[0]
 pool=str(pool).split()[0].split('_')[1]
 z=[]
 with open('/root/DGsetpool','w') as f:
  f.write('pool='+pool+'\n')
 owners=get('run',pool)
 owners=[x for x in owners if 'name' in str(x) ]
 owner=owners[0][0].split('/')[1]
 with open('/root/DGsetpool','a') as f:
  f.write('owner='+owner+'\n')
 myhost=hostname()
 with open('/root/DGsetpool','a') as f:
  f.write('myhost='+myhost+'\n')
 ownerip=get('leader',owner)
 if ownerip[0]== -1:
  ownerip=get('known',owner)
  if ownerip[0]== -1:
   return 3
 z=['/TopStor/pump.sh','VolumeCreateCIFS']
 for arg in args:
  z.append(arg)
 msg={'req': 'DGsetPool', 'reply':z}
 with open('/root/DGsetpool','a') as f:
  f.write('myhost='+ownerip[0][1]+' '+myhost+' '+str(z)+'\n')
 sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
 return 1

if __name__=='__main__':
 send(*sys.argv[1:])
