#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def broadcast(*args):
 z=[]
 knowns=[]
 myhost=hostname()
 for arg in args:
  z.append(arg)
 leaderinfo=get('leader','--prefix')
 knowninfo=get('known','--prefix')
 leaderip=leaderinfo[0][1]
 for k in knowninfo:
  knowns.append(k[1])
 print('leader',leaderip) 
 print('knowns',knowns) 
 msg={'req': z[0], 'reply':z[1:]}
 print('sending', leaderip, str(msg),'recevreply',myhost)
 sendhost(leaderip, str(msg),'recvreply',myhost)
 for k in knowninfo:
  sendhost(k[1], str(msg),'recvreply',myhost)

if __name__=='__main__':
 broadcast(*sys.argv[1:])
