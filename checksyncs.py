#!/bin/python3.6
from logqueue import queuethis
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from socket import gethostname as hostname

syncs = ['user']
myhost = hostname()
leader = get('leader','--prefix')[0][0].replace('leader/','')

def checksync():
 global syncs, myhost
 for sync in syncs:
   gsyncs = get('sync/'+sync,'--prefix') 
   print(gsyncs,gsyncs[0][1])
   maxgsync = max(gsyncs, key=lambda x: float(x[1]))
   mysync = [x for x in gsyncs if myhost in str(x) ]
   print('mysync',mysync)
   if len(mysync) > 0:
    mysync = float(mysync[0][1])
    if mysync != maxgsync[1]:
     if sync == 'user':
      print(maxgsync)
      put('sync/'+sync+'/'+myhost, str(maxgsync[1]))
      
 
if __name__=='__main__':
 checksync()
