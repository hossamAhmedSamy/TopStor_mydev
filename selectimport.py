#!/bin/python3.6
from etcddel import etcddel as etcddel
from etcdput import etcdput as put 
from etcdget import etcdget as get
from etcddel import etcddel as deli 
import socket, sys, subprocess
from sendhost import sendhost
from ast import literal_eval as mtuple
from zpooltoimport import zpooltoimport as importables

def importpls(*args):
 myhost=socket.gethostname()
 allinfo=get('to','--prefix')
 if(len(allinfo) > 0):
  running=get('hosts','--prefix')
  if(len(running) > 0):
   info=allinfo[0]
   zpool=info[1]
   zpool=mtuple(zpool)
   for z in zpool:
    if z['name'] not in str(running):
     owner=info[0].replace('toimport/','')
     ownerip=get('leader',owner)
     if ownerip[0]== -1:
      ownerip=get('known',owner)
     if ownerip[0]== -1:
      return 3
     deli('to',z['name']) 
     z=['/TopStor/pump.sh','Zpool','import','-f',z['name']]
     msg={'req': 'Zpool', 'reply':z}
     sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
     importpls(*args)
 return
if __name__=='__main__':
 importpls(*sys.argv[1:])
