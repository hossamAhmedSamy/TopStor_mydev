#!/usr/bin/python3
import subprocess,sys, os
import json
def takesnap(*args):
 os.environ['ETCDCTL_API']= '3'
 cmdline = ['/bin/etcdctl','--user=root:YN-Password_123','snapshot','restore','/TopStordata/etcdsnap.bak','--name dhcp32502','--data-dir /var/lib/etcd','--initial-advertise-peer-urls http://10.11.11.10:2380','--listen-peer-urls http://10.11.11.10:2380','--advertise-client-urls http://10.11.11.10:2379','--listen-client-urls http://10.11.11.10:2379','--initial-cluster dhcp32502=http://10.11.11.10:2380','--initial-cluster-state new','--initial-cluster-token token-01']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print(' '.join(cmdline))


if __name__=='__main__':
 takesnap(*sys.argv[1:])
