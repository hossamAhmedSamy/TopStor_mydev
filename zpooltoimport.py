#!/bin/python3.6
import subprocess, sys
from time import sleep
from socket import gethostname as hostname
from ioperf import ioperf
from logqueue import queuethis
from etcdput import etcdput as put
from etcdgetpy import etcdget as get 
from etcddel import etcddel as dels
from putzpoolfound import getpoolstoimport

def zpooltoimport(*args):
 myhost = hostname()
 needtoimport=get('needtoimport', myhost) 
 if myhost not in str(needtoimport):
  print('no need to import a pool here')
 else:
  for poolline in needtoimport:
   pool = poolline[0].replace('needtoimport/','')
   ioperf()
   cmdline= '/bin/zpool import  '+pool
   result = str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)
   if result.returncode == 0:
    sleep(3)
    dels('needtoimport', pool)
 if myhost not in str(get('leader','--prefix')):
  return
 pools = getpoolstoimport()
 for pool in pools:
  selectedhost = list(pool['currenthosts'])[0] 
  put('needtoimport/'+pool['name'], selectedhost)
 return
     
       
if __name__=='__main__':
 cmdline='cat /pacedata/perfmon'
 perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)
 if '1' in perfmon:
  queuethis('zpooltoimport.py','start','system')
 zpooltoimport(*sys.argv[1:])
 if '1' in perfmon:
  queuethis('zpooltoimport.py','stop','system')
