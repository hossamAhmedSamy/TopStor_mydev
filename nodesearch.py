#!/bin/python3.6
import nmap
import sys, subprocess

hostrange=sys.argv[1]
nm=nmap.PortScanner()
nm.scan(hostrange+'/24','22')
serverstatus='nothing'
#subprocess.run('export','ETCDCTL_API=3')
hostlist=[nm[x] for x in nm.all_hosts() if 'up' in nm[x]['status']['state']]
for host in hostlist:
 cmdline=['etcdctl','-w','json','--endpoints='+host['addresses']['ipv4']+':2379','member','list','2>/dev/null']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 if result.returncode==0:
  etcdserver=host
  serverstatus=result.stdout
serverstatus=str(serverstatus)[2:]
serverstatus=serverstatus[:-3]
etcdfile=open('/pacedata/runningetcdnodes.txt','w')
etcdfile.write(serverstatus)
etcdfile.close()
print(serverstatus)
