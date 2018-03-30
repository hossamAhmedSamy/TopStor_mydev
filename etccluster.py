#!/bin/python3.6
import subprocess
token=''
cluster_state='new'
hosts=[]
names=[]
cluster=''
etcfile=open('/pacedata/etcdnodes.txt')
for line in etcfile:
 print('line:',line)
 item=line.split();
 print('item',item)
 names.append(item[1])
 hosts.append(item[2])
 cluster=cluster+item[1]+'=http://'+item[2]+':2380,'
 if 'this' in line:
  token=item[0]
  thisname=item[1]
  thisip=item[2]

cmdline=['etcd', '--data-dir=data.etcd ','--name='+thisname,'--initial-advertise-peer-urls=http://'+thisip+':2380','--listen-peer-urls=http://'+thisip+':2380','--advertise-client-urls=http://'+thisip+':2379','--listen-client-urls=http://'+thisip+':2379','--initial-cluster='+cluster,'--initial-cluster-state='+cluster_state,'--initial-cluster-token='+token]
result=subprocess.run(cmdline,stdout=subprocess.PIPE,)
etcfile.close()
print(result.stdout)
