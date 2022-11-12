#!/usr/bin/python3
import subprocess,sys
from etcdget import etcdget as get
from etcdput import etcdput as put 
from time import time as stamp
from socket import gethostname as hostname

dev='enp0s8'
def updatenamespace(*args):
  myhost = hostname()
  put('namespace/mgmtip',args[0])
  put('sync/namespace/mgmtip_'+args[0]+'/request/'+myhost,'namespace_'+str(stamp()))
  put('sync/namespace/mgmtip_'+args[0]+'/request','namespace_'+str(stamp()))
  cmdline='/sbin/pcs resource update mgmtip ip='+args[0].split('/')[0]+' cidr_netmask='+args[0].split('/')[1]
  subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  cmdline='/sbin/ip addr del '+args[1].split('/')[0]+' dev '+dev
  subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  
if __name__=='__main__':
 updatenamespace(*sys.argv[1:])
