#!/usr/bin/python3
import subprocess,sys, datetime
from logqueue import queuethis
from etcdput import etcdput as put 
from time import sleep
from etcdputlocal import etcdput as putlocal
from etcdgetpy import etcdget as get 
from etcddel import etcddel as deli 
from socket import gethostname as hostname
import logmsg
def setall(*bargs):
 with open('/pacedata/perfmon','r') as f:
  perfmon = f.readline()
 if '1' in perfmon:
  queuethis('Evacuate','running','system')
 thehosts=get('modified','evacuatehost')
 if thehosts[0]==-1:
  if '1' in perfmon:
   queuethis('Evacuate','stop_cancel','system')
  return
 leader=get('leader','--prefix')[0][0].replace('leader/','')
 myhost=hostname()
 myip=get('ready',myhost)[0][1]
 for host in thehosts:
  hostn=host[0].split('/')[2]
  hostip=host[1]
  if myhost in hostn and myhost in leader:
   cmdline=['/TopStor/Converttolocal.sh',myip]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/TopStor/resettarget.sh',myhost]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  elif myhost in hostn and myhost not in leader:
   putlocal(myip,'toreset','yes')
   put('toremovereset/'+hostn,'reset')
   cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   cmdline=['/TopStor/resettarget.sh',myhost]
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   while True:
    cmdline=['/TopStor/rebootme','reset']
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    sleep(10)
   
   
  #elif hostn not in str(get('ready','--prefix')) and hostn not in str(get('lost','--prefix')) and myhost not in hostn and myhost in leader and hostn not in str(get('possible','--prefix')):
  elif myhost not in hostn and myhost in leader:
   put('toremovereset/'+hostn,'reset')
  hostreset=get('toremovereset/'+hostn,'reset')[0]
  if hostn in str(hostreset): 
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
    cmdline=['/pace/removetargetdisks.sh', hostn, hostip]
    result=subprocess.run(cmdline,stdout=subprocess.PIPE)
    for active in actives:
     activen=active[0].replace('ActivePartners/','')
     if activen not in str(dones) and activen not in str(thehosts): 
      print(activen,str(dones),str(thehosts))
      doneall=0
      break
    if doneall==1:
     frstnode=get('frstnode')[0]
     newnode=frstnode.replace('/'+hostn,'').replace(hostn+'/','')
     put('frstnode',newnode)
     deli("", hostn)
     put('tosync','yes')
     logmsg.sendlog('Evacuaesu01','info','system',hostn)
 if '1' in perfmon:
  queuethis('Evacuate','stop','system')
 return

if __name__=='__main__':
 setall(*sys.argv[1:])
