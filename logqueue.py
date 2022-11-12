#!/usr/bin/python3
import sys, datetime
from time import time
from etcdgetpy import etcdget as get
from etcdput import etcdput as put
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
from socket import gethostname as hostname

myhost = hostname()
def queuethis(*args):
 global myhost
 z=[]
 put('request/'+args[0]+'/'+myhost,args[1])
 myhost=hostname()
 dt=datetime.datetime.now().strftime("%m/%d/%Y")
 tm=datetime.datetime.now().strftime("%H:%M:%S")
 z=['/TopStor/logqueue2.sh', dt, tm, myhost ]
 for arg in args:
  z.append(arg)
 z.append(int(time()*1000))
 with open('/root/logqueuetmp','w') as f:
  f.write(str(z))
 leaderinfo=get('leader','--prefix')
 leaderip = leaderinfo[0][1]
 msg={'req': 'queue', 'reply':z}
 sendhost(leaderip, str(msg),'recvreply',myhost)
 
if __name__=='__main__':
 #queuethis('ddlrt.py','start','system')
 queuethis(*sys.argv[1:])
