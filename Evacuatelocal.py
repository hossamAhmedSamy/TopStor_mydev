#!/bin/python3.6
import subprocess,sys, datetime,socket
import json
from etcddellocal import etcddel as delilocal
from etcdputlocal import etcdput as putlocal 
import logmsg
def setall(*bargs):
 arg=bargs
 myhost=bargs[-4]
 name=bargs[-4]
 leader=bargs[-2]
 myip=bargs[-1]
 cmdline=['/TopStor/queuethis.sh','Evacuate.py','running',bargs[-1]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 with open('/root/evacuatelocal','w') as f:
  f.write('bargs'+str(bargs)+'\n')
 if myip in str(leader):
  with open('/root/evacuatelocal','a') as f:
   f.write('iamleader '+myip+' '+name+'\n')
  cmdline=['/TopStor/Converttolocal.sh',myip]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 putlocal(myip,'toreset','yes')
 putlocal(myip,'configured','no')
 with open('/root/evacuatelocal','a') as f:
  f.write('iamknown '+myip+' '+name+'\n')
 with open('/root/evacuatelocal','a') as f:
  f.write('rebooting '+myip+' '+name+'\n')
 cmdline=['/TopStor/rebootme','finished',bargs[-3]]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 return 1

if __name__=='__main__':
 setall(*sys.argv[1:])
