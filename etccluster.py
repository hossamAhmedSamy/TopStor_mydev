#!/bin/python3.6
import socket
token=''
cluster_state='new'
hosts=[]
names=[]
cluster=''
try:
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
 etcfile.close()
except:
  token='token-01'
  thisname=socket.gethostname()
  x=socket.getaddrinfo(thisname,None,socket.AF_INET, socket.SOCK_DGRAM,\
     socket.IPPROTO_IP, socket.AI_CANONNAME)
  z=[y for y in x if '127.0.0.1' not in str(y)]
  thisip=z[-1][-1][0]
  cluster=thisname+'=http://'+thisip+':2380'

cmdline=['name: '+thisname+'\n', 'data-dir: /var/lib/etcd\n', 'initial-advertise-peer-urls: http://'+thisip+':2380\n','listen-peer-urls: http://'+thisip+':2380\n','advertise-client-urls: http://'+thisip+':2379\n','listen-client-urls: http://'+thisip+':2379\n','initial-cluster: '+cluster+'\n','initial-cluster-state: '+cluster_state+'\n','initial-cluster-token: '+token+'\n']
with open('/etc/etcd/etcd.conf.yml','w') as f:
 f.writelines(cmdline)
