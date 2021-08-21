#!/bin/python3.6
import subprocess,sys, datetime
from logqueue import queuethis
from etcdput import etcdput as put 
from time import sleep
from etcdputlocal import etcdput as putlocal
from etcdget import etcdget as get 
from etcddel import etcddel as deli 
from socket import gethostname as hostname
import logmsg
def setall(*bargs):
 with open('/pacedata/perfmon','r') as f:
  perfmon = f.readline()
 if '1' in perfmon:
  queuethis('Evacuate','running','system')
 thehosts=get('toremove','start')
 if thehosts[0]==-1:
  if '1' in perfmon:
   queuethis('Evacuate','stop_cancel','system')
  return
 leader=get('leader','--prefix')[0][0].replace('leader/','')
 myhost=hostname()
 myip=get('ready',myhost)[0][1]
 print(myip,myhost,leader,str(thehosts))
 for host in thehosts:
  hostn=host[0].replace('toremove/','')
  hostip=get('ActivePartners/'+hostn)[0]
  if myhost in hostn and myhost in leader:
   cmdline=['/TopStor/Converttolocal.sh',myip]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  elif myhost in hostn and myhost not in leader:
   putlocal(myip,'toreset','yes')
   put('toremovereset/'+hostn,'reset')
   cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   while True:
    cmdline=['/TopStor/rebootme','reset']
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    sleep(10)
  if myhost not in hostn : 
     cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
     result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  logmsg.sendlog('Evacuaesu01','info','system',hostn)
 if '1' in perfmon:
  queuethis('Evacuate','stop','system')
 return

if __name__=='__main__':
 setall(*sys.argv[1:])
