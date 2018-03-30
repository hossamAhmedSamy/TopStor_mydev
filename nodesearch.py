#!/bin/python3.6
import nmap
import sys, subprocess

hostrange=sys.argv[1]
nm=nmap.PortScanner()
nm.scan(hostrange+'/24','22')
#subprocess.run('export','ETCDCTL_API=3')
for host in nm.all_hosts():
 print('checking:',host)
 cmdline=['etcdctl','-w','json','--endpoints='+host+':2379','member','list']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 if result.returncode==0:
  etcdserver=host
  serverstatus=result.stdout
serverstatus=str(serverstatus)[2:]
print('etcdserver',etcdserver,'\noutput:', str(serverstatus))
serverstatus=serverstatus[:-3]
print('etcdserver',etcdserver,'\noutput:', str(serverstatus))

