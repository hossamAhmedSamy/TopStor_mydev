#!/usr/bin/python3
import subprocess, sys
from ioperf import ioperf
from logqueue import queuethis, initqueue
from etcdput import etcdput as put
from etcdgetpy import etcdget as get 
from etcddel import etcddel as dels
from poolstoimport import getpoolstoimport, initgetpoolstoimport
from allphysicalinfo import getall 
from time import time as stamp
from time import sleep
from ast import literal_eval as mtuple


#leader=get('leader','--prefix')[0][0].split('/')[1]
stampi = str(stamp())

def selecthosting(minhost,hostname,hostpools):
 if len(hostpools) < minhost[1]:
  minhost = (hostname, len(hostpools))
 return minhost


def dosync(sync, *args):
  global leader, leaderip, myhost, myhostip, etcdip, stmapi
  #dels(leaderip, sync)  
  put(leaderip, *args)
  put(leaderip, args[0]+'/'+leader,args[1])
  return 

def selecthost(poolinfo,readies):
    global leader, leaderip, myhost, myhostip, etcdip, stmapi
    mincount = 1000000000 
    selectedhost = 'nohost'
    for hostinfo in readies:
        host = hostinfo[0].split('/')[1]
        if myhost == host and len(readies) > 1  :
            continue   ########  pass this since we are searching for the next host 
        counts = list(str(poolinfo['raids'])).count(host)
        if counts  < mincount:
            selectedhost =  host
            mincount = counts
        #elif selectedhost[0] == counts:
        #    selectedhost[1] = selectedhost[1] + [ host ]
    return selectedhost
        
def zpooltoimport(*args):
 global leader, leaderip, myhost, myhostip, etcdip
 if args[0]=='init':
     leader = args[1]
     leaderip = args[2]
     myhost = args[3]
     myhostip = args[4]
     etcdip = args[5]
     initqueue(leaderip, myhost) 
     initgetpoolstoimport(leader,leaderip,myhost,myhostip)
     return
 poouids = get(etcdip,'poouids',myhost) 
 nextpools=get(leaderip, 'poolnxt', '--prefix') 
 if 'not reachable' in str(nextpools):
        return
 needtoimport=[ x for x in nextpools if myhost in str(x)] 
 pools = [v for k,v in getall(leaderip)['pools'].items()]
 mypools = [v  for v in pools if v['host'] == myhost ]
 if 'not reachable' in str(pools):
        return
 if '_1' in str(poouids):
    poouids = []
 for poo in poouids:
    print('poouids start')
    pool=poo[0].split('/')[1]
    if pool in str(mypools):
        cmdline = 'zpool reguid '+pool
        result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
        if result.returncode == 0:
            print('done')
            cmdline="zpool get guid "+pool+" -H "
            guid=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split()[2]

            dels(leaderip,'sync/ActPool', pool)
            put(leaderip,'ActPool/'+pool,guid)
            dosync('actpool_', 'sync/ActPool/Add_'+pool+'_'+guid+'/request','actpool_'+str(stamp()))
            dels(etcdip, 'poouids/'+pool) 
        else:
            print('pool not ready yet')
 if myhost not in str(needtoimport):
  print(needtoimport)
  print('no need to import a pool here')
                  
 else:
  for poolline in needtoimport:
   pool = poolline[0].replace('poolnxt/','')
   if pool in str(pools):
    continue
   ioperf(leaderip, myhost)
   print('pool to be imported now', pool)
   poolid = get(leaderip,'ActPool/'+pool)[0]
   if poolid == '_1':
    poolid = pool
   cmdline= '/usr/sbin/zpool import '+poolid
   dels(leaderip, 'poolnxt', pool ) 
   print(cmdline)
   put(leaderip, 'pools/'+pool,myhost)
   res = subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
   result = res.stdout.decode('utf-8')
   sleep(1)
   cmdline= '/usr/sbin/zpool status  '
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   print('result',result)
   if pool in result:
    put(etcdip, 'dirty/volume','0')
    put(etcdip, 'poouids/'+pool,myhost)
    print('before sync')
    print('sync pools Add')
    dels(leaderip,'sync/pools', pool)
    dosync('pools_', 'sync/pools/Add_'+pool+'_'+myhost+'/request','pools_'+str(stamp()))
    print('pools_', 'sync/pools/Add_'+pool+'_'+myhost+'/request','pools_'+str(stamp()))
    print('After sync')
    #cmdline= 'systemctl restart zfs-zed  '
    #result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   else:
    dels(leaderip, 'pools/',pool)
        
   dels(leaderip, 'poolnxt',pool)
    
 if myhost != leader:
  return

 readies=get(etcdip,'ready','--prefix')
 hosts=get(leaderip,'host','/current')
 
 #pools = [poolinfo[0].split('/')[1]+'_'+poolinfo[1] for poolinfo in pools ]
 activepools = get(leaderip, 'ActPool','--prefix')
 notactivepools = getpoolstoimport()
 cpools = pools
 for notpo in notactivepools:
    notpname = notpo['name']
    notpid = notpo['guid'] 
    if (notpname in str(activepools) and (notpid in str(activepools) or len(readies) == 1)) or notpname not in str(activepools): 
        cpools = cpools + [notpo] 
    if len(readies) == 1:
        dels(leaderip, 'ActPool/'+notpname)
 
 for poolinfo in cpools:
    pool = poolinfo['name']
    if 'pree' in pool:
     continue
    if pool not in str(needtoimport):
        nxthost=selecthost(poolinfo,readies)
        print('nxthosts',nxthost)
        poolnxt=get(leaderip,'poolnxt/'+pool)[0]
        if poolnxt in str(nxthost):
            continue 
        print('adding')
        #dels(leaderip,'poolnxt/'+pool)
        put(leaderip,'poolnxt/'+pool,nxthost)
        print('sync poolnxt Add',nxthost,pool)
        dels(leaderip,'sync/poolnxt',pool)
        dosync('poolnxt', 'sync/poolnxt/Add_'+pool+'_'+nxthost+'/request','poolnxt_'+str(stamp()))
 return
     
       
if __name__=='__main__':
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leader'
    leader=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py leaderip'
    leaderip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternode'
    myhost=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    cmdline='docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip'
    myhostip=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').replace('\n','').replace(' ','')
    if leader == myhost:
        etcdip = leaderip 
    else:
        etcdip = myhostip
    initqueue(leaderip, myhost) 
    initgetpoolstoimport(leader,leaderip,myhost,myhostip)
    zpooltoimport('hi')
 #cmdline='cat /pacedata/perfmon'
 #perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)
 #if '1' in perfmon:
 # queuethis('zpooltoimport.py','start','system')
 #if '1' in perfmon:
 # queuethis('zpooltoimport.py','stop','system')
