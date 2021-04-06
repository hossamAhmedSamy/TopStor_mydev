#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def send(*bargs):
 cmdline=['/TopStor/queuethis.sh','DGsetPool.py','running',bargs[-1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 if(len(bargs) < 3):
  args=bargs[0].split()
 else:
  args=bargs
 pool=args[-2]
 #pool=str(pool).split()[-1]
 with open('/root/DGsetpool','w') as f:
  f.write('args='+str(args)+'\n')
 z=[]
 with open('/root/DGsetpool','a') as f:
  f.write('pool='+pool+'\n')
 owner=args[-1]
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
 print('owner',ownerip[0])
 z=['/TopStor/pump.sh','DGsetPool']
 for arg in args[:-1]:
  z.append(arg)
 msg={'req': 'DGsetPool', 'reply':z}
 sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
 with open('/root/DGsetpool','a') as f:
  f.write('myhost='+ownerip[0][1]+' '+str(msg)+' recvreply '+myhost+'\n')
 cmdline=['/TopStor/queuethis.sh','DGsetPool.py','stop',bargs[-1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 return 1

if __name__=='__main__':
 send(*sys.argv[1:])
