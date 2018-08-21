#!/bin/python3.6
import subprocess,sys
from etcdget import etcdget as get
import json
def setnamespace(*args):
 nslist=get('namespace','--prefix')
 ns=(x for x in nslist)
 for arg in args:
  try: 
   nsn=next(ns)
  except: 
   return
  cmdline='/sbin/pcs resource create '+nsn[0].replace('namespace/','')+' ocf:heartbeat:IPaddr2 nic='+arg+' ip='+nsn[1]+' cidr_netmask=24 op monitor on-fail=restart'
  subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  cmdline='/sbin/pcs resource group add namespaces '+nsn[0].replace('namespace/','')
  subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
if __name__=='__main__':
 setnamespace(*sys.argv[1:])
