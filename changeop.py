#!/bin/python3.6
import subprocess,sys
import json
from ast import literal_eval as mtuple
from etcdget import etcdget as get
from etcdput import etcdput as put
from selectspare import getall
from selectspare import putall
from selectspare import delall
import logmsg
def changeop(*args):
 alls=getall(args[0])
 if type(alls) != dict :
  return -1
 if len(args) > 1:
  if args[1] == 'old':
   putall(args[0],'old')
   return 1
 oldlls=getall(args[0],'old')
 if type(oldlls) != dict :
  for disk in alls['defdisks']:
   logmsg.sendlog('Diwa1','warning','system', disk['id'], disk['changeop'])
   cmdline='/sbin/zpool offline '+disk['pool']+' '+disk['name']
   subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
  putall(args[0],'old')
  return
 changeddisks={k:alls[k] for k in alls if alls[k] != oldlls[k] and 'disk' in k} 
 print('changed',len(changeddisks))
 if len(changeddisks) > 0:
  delall(args[0],'old')
 


if __name__=='__main__':
 changeop(*sys.argv[1:])
