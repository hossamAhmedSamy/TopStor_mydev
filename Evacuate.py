#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from etcdput import etcdput as put 
from etcddel import etcddel as deli 
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from broadcast import broadcast as broadcast 
from sendhost import sendhost
from time import sleep
import logmsg
def sendlog(*args):
 z=[]
 knowns=[]
 myhost=hostname()
 logmsg.sendlog('Evacuaest01','info',args[-1],args[-2])
 broadcast('RemoveTargets', args[-2])
 z=['/TopStor/Evacuatelocal.py']
 with open('/root/evacuate','w') as f:
  f.write('bargs'+str(args)+'\n')
 for arg in args:
  z.append(arg)
 hostip=get('ActivePartners/'+args[-2])
 losts=get('lost','--prefix')
 knowns=get('knwon','--prefix')
 readys=get('ready','--prefix')
 theleader=get('leader','--prefix')[0]
 nextleader=theleader[0].replace('leader/','') 
 leader=theleader[1]
 if args[-2] in str(nextleader):
  isleader=1
  nextleader=get('nextlead')[0].split('/')[0]
 if args[-2] in str(readys):
  z.append(leader)
  z.append(hostip)
  msg={'req': 'Evacuate', 'reply':z}
  sendhost(hostip[0], str(msg),'recvreply',myhost)
 isleader=1
 while isleader:
  print('still leader')
  sleep(2)
  leader=get('leader','--prefix')
  if nextleader in str(leader):
   isleader=0
 sleep(2)
 frstnode=get('frstnode')
 newnode=frstnode[0].replace('/'+args[-2],'').replace(args[-2]+'/','')
 put('frstnode',newnode)
 deli('',args[-2])
 put("tosync","yes")

if __name__=='__main__':
 sendlog(*sys.argv[1:])
