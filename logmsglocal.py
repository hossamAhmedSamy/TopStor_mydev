#!/usr/bin/python3
import subprocess,sys, datetime
import json
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from ast import literal_eval as mtuple
from sendhost import sendhost

leaderip = ''
myhsot = ''
def initlog(ldr,host,etcd):
    global leaderip, myhost, etcdip
    leaderip = ldr
    myhost = host
    etcdip = etcd

def sendlog(*args):
 global leaderip, myhost, etcdip
 z=[]
 knowns=[]
 dt=datetime.datetime.now().strftime("%m/%d/%Y")
 tm=datetime.datetime.now().strftime("%H:%M:%S")
 z=['/TopStor/logmsg2.sh', dt, tm, myhost ]
 for arg in args:
  z.append(arg)
 knowninfo=get(etcdip, 'known','--prefix')
 for k in knowninfo:
  knowns.append(k[1])
 msg={'req': 'msg2', 'reply':z}
 put(leaderip, 'notification',' '.join(z))
 sendhost(leaderip, str(msg),'recvreply',myhost)
 for k in knowninfo:
  sendhost(k[1], str(msg),'recvreply',myhost)
  knowns.append(k[1])

if __name__=='__main__':
 etcdip = sys.argv[1]
 initlog(get(etcdip, 'leaderip')[0], get(etcdip, 'clusternode')[0])
 sendlog(*sys.argv[2:])
