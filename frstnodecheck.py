#!/usr/bin/python3
import sys, subprocess, socket
from etcdgetpy import etcdget as get

myhost=socket.gethostname()
leader=get('leader','--prefix')
print('leader', leader)
if myhost in str(leader):
 frstnode=get('frstnode')[0].split('/')[0]
 if myhost not in frstnode:
  frstnodeip=get('Active',frstnode)[0][1]
  cmdline=['etcdctl','-w','json','--endpoints='+frstnodeip+':2379','member','list']
  result=subprocess.run(cmdline,stdout=subprocess.PIPE)
  if result.returncode==0:
   cmdline=['/TopStor/rebootme']
   result=subprocess.run(cmdline,stdout=subprocess.PIPE)
