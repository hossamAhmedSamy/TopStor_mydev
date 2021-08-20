#!/bin/python3.6
import subprocess, socket, binascii
from logqueue import queuethis
from sendhost import sendhost
from etcdput import etcdput as put
from etcdgetpy import etcdget as get 
from etcddel import etcddel as deli 
from broadcast import broadcast as broadcast 
from os import listdir as listdir
from os import remove as remove
from putzpoolimport import putzpoolimport as putz, listpools
from poolall import getall as getall
from os.path import getmtime as getmtime
import sys, datetime
import logmsg

def zpooltoimport(*args):
 cmdline='/TopStor/CheckPoolimport user=system'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 myhost=socket.gethostname()
 pools=listpools() 
 if len(pools) > 0:
  loads = get('cpu','--prefix')
  loads = [(x[0].replace('cpuperf/',''),x[1]) for x in loads ]
  hostsdict = {}
  for load in loads:
   hostsdict[load[0]] = load[1]
  for pool in pools:
   if myhost in pools[pool]:
    poolhosts = []
    for host in pools[pool]:
     poolhosts.append((host,hostsdict[host])) 
    poolhosts.sort(key=lambda x: x[1])
    if poolhosts[0][0] == myhost:
     cmdline='/TopStor/importthis.sh '+pool
     result=subprocess.check_output(cmdline.split(),stderr=subprocess.STDOUT).decode('utf-8')
     deli('poollock/'+pool,myhost)
     if 'ok' in result:
      put('poolready/'+pool,myhost)
      broadcasttolocal('poolready/'+pool,myhost)
     
       
if __name__=='__main__':
 cmdline='cat /pacedata/perfmon'
 perfmon=str(subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout)
 if '1' in perfmon:
  queuethis('zpooltoimport.py','start','system')
 zpooltoimport(*sys.argv[1:])
 if '1' in perfmon:
  queuethis('zpooltoimport.py','stop','system')
