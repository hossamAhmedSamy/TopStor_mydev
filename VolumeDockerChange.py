#!/bin/python3.6
import subprocess,sys, os
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from broadcasttolocal import broadcasttolocal 

from socket import gethostname as hostname



def delcifs(*args):
 vol = args[0]
 ipaddr = args[1]
 cmdline = 'docker ps -f volume='+vol
 print(cmdline)
 dockers = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
 dockers = [ x for x in dockers if ipaddr not in x and 'CONTAINER' not in x and len(x) > 10]
 print('dockers',dockers)
 print('###############3')
 for docker in dockers:
   res = docker.split()[-1]
   cmdline = 'docker rm -f '+res
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   cmdline = '/sbin/pcs resource delete --force '+res
   result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
   
   
if __name__=='__main__':
 delcifs(*sys.argv[1:])
