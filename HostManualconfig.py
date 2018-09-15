#!/bin/python3.6
import subprocess,sys, datetime,socket
import json
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
import logmsg
def setall(*bargs):
 with open('/root/tmp','w') as f:
  f.write(str(bargs))
 myhost=socket.gethostname()
 arg=bargs[0].split()
 owner=''
 name='.'
 msg={}
 for x in arg[:-1]:
  if 'hostname' in x:
    x=x.split(':')
    owner=x[1]
 with open('/root/tmp','a') as f:
  f.write(name+owner+'\n')
 name=get('alias/'+owner)
 with open('/root/tmp','a') as f:
  f.write(name[0]+owner+arg[-1]+'\n')
 logmsg.sendlog('HostManual1004','info',arg[-1],str(name[0]))
 z=['/TopStor/pump.sh','LocalManualConfig.py']
 for aarg in arg:
  z.append(aarg)
 msg={'req': 'LocalManualConfig', 'reply':z}
 ownerip=get('leader',owner)
 if ownerip[0]== -1:
  ownerip=get('known',owner)
  if ownerip[0]== -1:
   return 3
 with open('/root/HostManualconfigtmp','w') as f:
  f.write('owner '+owner+"\n")
  f.write('ownerip '+ownerip[0][1]+"\n")
  f.write('msg '+str(msg)+"\n")
 sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
 return 1

if __name__=='__main__':
 setall(*sys.argv[1:])
