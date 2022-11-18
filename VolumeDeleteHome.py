#!/usr/bin/python3
import subprocess,sys, datetime
import json
from etcdgetpy import etcdget as get
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
 z=[]
 owner=get('pools/'+pool)[0]
 myhost=hostname()
 ownerip=get('leader',owner)
 if ownerip[0]== -1:
  return 3
 z=['/TopStor/pump.sh','VolumeDeleteHome']
 for arg in args:
  z.append(arg)
 msg={'req': 'VolumeDelete', 'reply':z}
 sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
 return 1

if __name__=='__main__':
 send(*sys.argv[1:])
