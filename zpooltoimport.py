#!/bin/python3.6
import subprocess, socket, binascii
from etcdput import etcdput as put
from etcdget import etcdget as get 
from broadcast import broadcast as broadcast 
from os import listdir as listdir
from os import remove as remove
from poolall import getall as getall
from os.path import getmtime as getmtime
import sys
import logmsg

def zpooltoimport(*args):
 myhostpools=[]
 with open('/root/toimport','w') as f:
  f.write('starting to scan for import \n')
 myhost=socket.gethostname()
 runningpools=[]
 readyhosts=get('ready','--prefix')
 deletedpools=get('delet','--prefix')
 cannotimport=get('cannotimport/'+myhost,'--prefix')
 deletedpools=deletedpools+cannotimport
 with open('/root/toimport','a') as f:
  f.write('readyhosts='+str(readyhosts)+'\n')
 for ready in readyhosts:
  ready=ready[0].replace('ready/','')
  with open('/root/toimport','a') as f:
   f.write('readyhost='+str(ready)+'\n')
  x=getall(ready)
  myhostall=x
  with open('/root/toimport','a') as f:
   f.write('xall='+str(x)+'\n')
  x=getall(ready)['pools']
  if ready == myhost:
   myhostpools=x
  with open('/root/toimport','a') as f:
   f.write('xpool='+str(x)+'\n')
  runningpools.append(getall(ready)['pools'])
  with open('/root/toimport','a') as f:
   f.write('updated runningpools='+str(runningpools)+'\n')
 pools=[f for f in listdir('/TopStordata/') if 'pdhcp' in f and f not in str(runningpools) and f not in str(deletedpools) and 'pree' not in f ]
 with open('/root/toimport','a') as f:
  f.write('stored pool db'+str(pools)+'\n')
 logmsg.sendlog('Zpst01','info','system')
 mydisks=getall(myhost)['disks']
 mydisks=[(x['name'],x['status'],x['changeop']) for x in mydisks if 'ONLINE' not in x['status']]
 with open('/root/toimport','a') as f:
  f.write('all my disks'+str(mydisks)+'\n')
 pooltoimport=[]
 for pool in pools:
  cmdline='/sbin/zpool import -c /TopStordata/'+pool
  result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
  pooldisks=[x.split()[0] for x in str(result)[2:][:-3].replace('\\t','').split('\\n') if 'scsi' in x ]
  with open('/root/toimport','a') as f:
   f.write('pool'+str(pool)+' disks '+str(pooldisks)+'\n')
  count=0
  for disk in pooldisks:
   if disk in str(mydisks):
    count+=1
  if count > 0:
   with open('/root/toimport','a') as f:
    f.write('identified '+str(pool)+' to import \n')
   pooltoimport.append((pool,len(pooldisks),count))
 print(pooltoimport)
 with open('/root/toimport','a') as f:
  f.write('all pools to import'+str(pooltoimport)+'\n')
 if len(pooltoimport) > 0:
  put('toimport/'+myhost,str(pooltoimport))
  logmsg.sendlog('Zpsu01','info','system',':found')
 else:
  for pool in pools:
   remove('/TopStordata/'+pool)
  for pool in myhostpools:
   if pool['name']=='pree' :
    continue
   cachetime=getmtime('/TopStordata/'+pool['name'])
   if cachetime==pool['timestamp']:
    continue 
   bpoolfile=''
   with open('/TopStordata/'+pool['name'],'rb') as f:
    bpoolfile=f.read()
   poolfile=binascii.hexlify(bpoolfile)
   broadcast('Movecache','/TopStordata/'+pool['name'],poolfile) 
  put('toimport/'+myhost,'nothing')
  logmsg.sendlog('Zpsu01','info','system',':nothing')
 return pooltoimport 

if __name__=='__main__':
 zpooltoimport(*sys.argv[1:])

