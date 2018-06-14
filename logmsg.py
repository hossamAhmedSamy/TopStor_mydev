#!/bin/python3.6
import subprocess,sys
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def sendlog(*args):
 z=[]
 myhost=hostname()
 z.append('/TopStor/logmsg2.sh')
 z.append(myhost)
 for arg in args:
  z.append(arg)
 print('z=',z)
 leaderinfo=get('leader','--prefix')
 leader=leaderinfo[0][0].split('/')[1]
 leaderip=leaderinfo[0][1]
 print('leader',leaderip) 
 msg={'req': 'msg2', 'reply':z}
 print('sending')
 sendhost(leaderip, str(msg),'recvreply',myhost)

if __name__=='__main__':
 sendlog(*sys.argv[1:])
