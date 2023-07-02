#!/usr/bin/python3
import subprocess,sys, datetime
from logqueue import queuethis, initqueue
from etcdput import etcdput as put 
from time import sleep
from etcdputlocal import etcdput as putlocal
from etcdgetpy import etcdget as getp 
from etcdgetlocalpy import etcdget as get
from etcddel import etcddel as deli 
from etcddellocal import etcddel as delilocal 
from socket import gethostname as hostname
import logmsg
def setall(*bargs):
 with open('/pacedata/perfmon','r') as f:
  perfmon = f.readline()
 if '1' in perfmon:
  queuethis('Evacuate','running','system')
 myhost = bargs[1] 
 leaderip = bargs[0] 
 logmsg.initlog(leaderip, myhost)
 initqueue(leaderip, myhost)

 myip = get(leaderip,'ready/'+myhost)[0]
 hostn=bargs[2]
 hostip=bargs[3]
 userreq=bargs[-1]
 print('hihih',hostip, hostn)
 leader=get('leader','--prefix')[0][0].split('/')[1]
 print('iiiiiiiiiiiiiiiii',hostn,myhost, leader, hostip)
 if myhost in hostn:
  if myhost in leader:
   print('iam the leader and the one to evacuate')
   cmdline=['/TopStor/Converttolocal.sh',myip]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  cmdline=['/TopStor/resettarget.sh',myhost]
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  delilocal("",hostn)
  delilocal("sync","--prefix")
  while True:
   cmdline=['/TopStor/rebootme','reset']
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   sleep(10)
 else:
  if myhost in leader:
    print('iam here', hostn, hostip)
    cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    deli(leaderip, "",hostn)
  else:
    cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    delilocal("",hostn)
    delilocal("sync","--prefix")
 logmsg.sendlog('Evacuaesu01','info',userreq ,hostn)
 if '1' in perfmon:
  queuethis('Evacuate','stop','system')
 return

if __name__=='__main__':
 setall(*sys.argv[1:])
