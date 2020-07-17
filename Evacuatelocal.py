#!/bin/python3.6
import subprocess,sys, datetime,socket
import json
from etcddel import etcddel as deli
from etcdget import etcdget as get 
from etcdputlocal import etcdput as putlocal 
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
import logmsg
def setall(*bargs):
 arg=bargs
 name=bargs[-2]
 cmdline=['/TopStor/queuethis.sh','Evacuate.py','running',bargs[-1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 logmsg.sendlog('Evacuaest01','info',arg[-1],name)
 with open('/root/evacuatelocal','w') as f:
  f.write('bargs'+str(bargs)+'\n')
 myhost=socket.gethostname()
 lost=get('lost','--prefix')
 if name in str(lost):
  deli("",name)
 else:
  hostip=get('ActivePartners/'+name)
  leader=get('leader','--prefix')
  if name in str(leader):
   put('configured','no')
  else:
   putlocal(hostip[0],'configured','no')
  if myhost in str(leader):
   with open('/root/evacuatelocal','a') as f:
    f.write('iamleader '+name+'\n')
   deli("",name)
  else:
   myip=get('ready/'+myhost)
   with open('/root/evacuatelocal','a') as f:
    f.write('iamknown '+myip[0]+' '+arg[-2]+'\n')
   delilocal(myip[0],"",name)
   logmsg.sendlog('Evacuaesu01','info',arg[-1],name)
   cmdline=['/TopStor/queuethis.sh','Evacuate.py','finished',bargs[-1]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  if myhost in  name:
   cmdline=['/TopStor/rebootme','finished',bargs[-1]]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 return 1

if __name__=='__main__':
 setall(*sys.argv[1:])
