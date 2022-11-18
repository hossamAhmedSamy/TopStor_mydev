#!/usr/bin/python3
import subprocess,sys, datetime
from time import time
from etcdget import etcdget as get
from logqueue import queuethis
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def syncpls(*args):
 z=[]
 with open('/pacedata/perfmon') as f:
  perfmon = f.readline()
 if perfmon:
  queuethis('syncqueue','nextlead_queue','system')
 myhost=hostname()
 cmdline=['wc','-l','/TopStordata/taskperf']
 currentlines=str(subprocess.run(cmdline,stdout=subprocess.PIPE).stdout).replace("b'",'').split(' ')[0]
 print(currentlines) 
 z=['/TopStor/pump.sh','syncqueue.py', str(currentlines)]
 for arg in args:
  z.append(arg)
 leaderinfo=get('leader','--prefix')
 leaderip = leaderinfo[0][1]
 print('leader',leaderip) 
 msg={'req': 'synq', 'reply':z}
 print('sending', leaderip, str(msg),'recevreply',myhost)
 sendhost(leaderip, str(msg),'recvreply',myhost)
 
if __name__=='__main__':
 #queuethis('ddlrt.py','start','system')
 syncpls(*sys.argv[1:])
