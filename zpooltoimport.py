#!/bin/python3.6
import subprocess, socket
from etcdput import etcdput as put
from etcdget import etcdget as get 
from os import listdir
from selectspare import getall
import sys

def zpooltoimport(*args):
 myhost=socket.gethostname()
 runningpools=[]
 readyhosts=get('ready','--prefix')
 for ready in readyhosts:
  ready=ready[0].replace('ready/','')
  runningpools.append(getall(ready)['pools'])
 pools=[f for f in listdir('/TopStordata/') if 'pdhcp' in f and f not in str(runningpools) and 'pree' not in f ]
 mydisks=getall(myhost)['disks']
 mydisks=[(x['name'],x['status'],x['changeop']) for x in mydisks if 'ONLINE' not in x['status']]
 pooltoimport=[]
 for pool in pools:
  cmdline='/sbin/zpool import -c /TopStordata/'+pool
  result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
  pooldisks=[x.split()[0] for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'scsi' in x ]
  count=0
  for disk in pooldisks:
   if disk in str(mydisks):
    count+=1
  pooltoimport.append((pool,len(pooldisks),count))
 print(pooltoimport)
 put('toimport/'+myhost,str(pooltoimport))
 return pooltoimport 

if __name__=='__main__':
 zpooltoimport(*sys.argv[1:])
