#!/bin/python3.6
import subprocess, socket, binascii
from sendhost import sendhost
from etcdput import etcdput as put
from etcdget import etcdget as get 
from etcddel import etcddel as deli 
from broadcast import broadcast as broadcast 
from os import listdir as listdir
from os import remove as remove
from putzpoolimport import putzpoolimport as putz
from poolall import getall as getall
from os.path import getmtime as getmtime
import sys, datetime
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
 importedpools=get('pools/','--prefix')
 lockedpools=get('lockedpools','--prefix')
 deletedpools=deletedpools+cannotimport+importedpools
 timestamp=int(datetime.datetime.now().timestamp())-5
 for poolinfo in lockedpools:
  pool=poolinfo[0].split('/')[1]
  logmsg.sendlog('Zpwa01','info','system',pool)
  print('in locked')
  oldtimestamp=poolinfo[1].split('/')[1]
  lockhost=poolinfo[1].split('/')[0]
  lockhostip=get('leader/'+lockhost)
  if( '-1' in str(lockhostip)):
   lockhostip=get('known/'+lochost)
   if('-1' in str(lockhostip)):
    deli('lockedpools/'+pool)
    continue
  print('in locked')
  if(int(timestamp) > int(oldtimestamp)):
   put('lockedpools/'+pool,lockhost+'/'+str(timestamp))
   z=['/TopStor/pump.sh','ReleasePoolLock',pool]
   msg={'req': 'ReleasePoolLock', 'reply':z}
   sendhost(lockhostip[0], str(msg),'recvreply',myhost)
   print('here',lockhostip[0])

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
 #pools=[f for f in listdir('/TopStordata/') if 'pdhcp' in f and f not in str(runningpools) and f not in str(deletedpools) and 'pree' not in f ]
 waitingpools=putz() 
 print('waiting',waitingpools)
 pools=[f['name'] for f in waitingpools if f['name'] not in str(runningpools) and f['name'] not in str(deletedpools) ]
 with open('/root/toimport','a') as f:
  f.write('stored pool db'+str(pools)+'\n')
 logmsg.sendlog('Zpst01','info','system')
 mydisks=getall(myhost)['disks']
 mydisks=[(x['name'],x['status'],x['changeop']) for x in mydisks if 'ONLINE' not in x['status']]
 with open('/root/toimport','a') as f:
  f.write('all my disks'+str(mydisks)+'\n')
 pooltoimport=[]
 for pool in pools:
  #cmdline='/sbin/zpool import -c /TopStordata/'+pool
  cmdline='/sbin/zpool import '+pool
  print('checking pool: ',str(pool))
  result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
  if 'insufficient replicas' in str(result):
   print('pool cannot be imported now')
   put('cannotimport/'+myhost+'/'+pool,'1') 
   deli('lockedpools',str(pool)) 
   logmsg.sendlog('Zpfa02','warning','system',str(pool))
   continue
  else:
   cmdline='/TopStor/VolumeActivateCIFS  pool='+pool+' user=system'
   result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
   cmdline='/TopStor/VolumeActivateNFS  pool='+pool+' user=system'
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
 with open('/root/toimport','a') as f:
  f.write('all pools to import'+str(pooltoimport)+'\n')
 if len(pooltoimport) > 0:
  alreadyfound=get('toimport/'+myhost)
  for pool in pools:
   if str(pool) in str(lockedpools):
    continue
   if str(pool) not in alreadyfound:
    put('toimport/'+myhost,str(pooltoimport))
    logmsg.sendlog('Zpsu01','info','system',':found')
    print('toimport:',str(pooltoimport))
    exit()
 else:
  #for pool in pools:
  # remove('/TopStordata/'+pool)
  for pool in myhostpools:
   if pool['name']=='pree' :
    continue
   if pool['name'] in str(lockedpools) :
    continue
   cachetime=getmtime('/TopStordata/'+pool['name'])
   if cachetime==pool['timestamp']:
    continue 
   bpoolfile=''
   with open('/TopStordata/'+pool['name'],'rb') as f:
    bpoolfile=f.read()
   poolfile=binascii.hexlify(bpoolfile)
   broadcast('Movecache','/TopStordata/'+pool['name'],str(poolfile))
  put('toimport/'+myhost,'nothing')
  logmsg.sendlog('Zpsu01','info','system',':nothing')
 return pooltoimport 

if __name__=='__main__':
 zpooltoimport(*sys.argv[1:])
