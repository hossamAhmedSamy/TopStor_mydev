#!/bin/python3.6
import subprocess,sys, datetime
from etcdput import etcdput as put 
from etcdputlocal import etcdput as putlocal
from etcdget import etcdget as get 
from etcddel import etcddel as deli 
from socket import gethostname as hostname
import logmsg
def setall(*bargs):
 thehosts=get('toremove','start')
 if thehosts[0]==-1:
  return
 leader=get('leader','--prefix')[0][0].replace('leader/','')
 myhost=hostname()
 myip=get('ready',myhost)[0][1]
 print(myip,myhost,leader,str(thehosts))
 for host in thehosts:
  hostn=host[0].replace('toremove/','')
  hostip=get('ActivePartners/'+hostn)
  if myhost in hostn and myhost in leader:
   cmdline=['/TopStor/Converttolocal.sh',myip]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  if myhost in hostn and myhost not in leader:
   putlocal(myip,'toreset','yes')
   put('toremove/'+hostn,'reset')
   cmdline=['/TopStor/rebootme','finished']
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  if myhost not in hostn : 
   hosts=get('toremove/'+hostn,'done')
   if myhost not in str(hosts):
    put('toremove/'+hostn+'/'+myhost,'done')
    cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  if myhost not in hostn and myhost in leader:
   actives=get('Active','--prefix')
   dones=get('toremove/'+hostn,'done')
   doneall=1
   hostreset=get('toremove/'+hostn,'reset')[0]
   for active in actives:
    activen=active[0].replace('ActivePartners/','')
    if activen not in str(dones) and activen not in str(thehosts) and hostn in hostreset: 
     print(activen,str(dones),str(thehosts))
     doneall=0
     break
   if doneall==1:
    deli("", hostn)
    put('tosync','yes')
    logmsg.sendlog('Evacuaesu01','info','system',hostn)
 return

if __name__=='__main__':
 setall(*sys.argv[1:])
