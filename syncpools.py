#!/bin/python3.6
import subprocess, socket, binascii
from etcdput import etcdput as put
from etcdget import etcdget as get 
from broadcast import broadcast as broadcast 
from os import listdir
from os import remove 
from poolall import getall as getall
from os.path import getmtime
import sys
import logmsg

def syncmypools(*args):
 logmsg.sendlog('Zpst03','info','system')
 myhostpools=[]
 myhost=socket.gethostname()
 runningpools=[]
 readyhosts=get('ready','--prefix')
 myhostpools=getall(myhost)['pools']
 for pool in myhostpools:
  if pool['name']=='pree' :
   continue
  cachetime=getmtime('/TopStordata/'+pool['name'])
  if cachetime==pool['timestamp']:
    continue 
  bpoolfile=''
  with open('/TopStordata/'+pool['name'],'rb') as f:
   bpoolfile=f.read()
  poolfile=binascii.hexlify(bpoolfile)
  broadcast('Movecache','/TopStordata/'+pool['name'],poolfile) 
 logmsg.sendlog('Zpsu03','info','system')
 return 

if __name__=='__main__':
 syncmypools(*sys.argv[1:])

