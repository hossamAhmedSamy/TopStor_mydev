#!/bin/python3.6
import subprocess,sys, datetime,socket
from logqueue import queuethis
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
import logmsg
def setall(*bargs):
 queuethis('HostManualconfig.py','running',bargs[-1])
 with open('/root/tmp','w') as f:
  f.write('bargs'+str(bargs)+'\n')
 myhost=socket.gethostname()
 arg=bargs
 owner=''
 name='.'
 msg={}
 for x in arg[:-1]:
  if 'hostname' in x:
    x=x.split(':')
    owner=x[1]
  with open('/root/tmp','a') as f:
   f.write('name='+name+'\n')
   f.write('owner='+owner+'\n')
   f.write('x='+str(x)+'\n')
 name=get('alias/'+owner)
 name=str(name[0])
 with open('/root/tmp','a') as f:
  f.write('name_owner_admin='+name+'_'+owner+'_'+arg[-1]+'\n')
 logmsg.sendlog('HostManual1004','info',arg[-1],name)
 z=['/TopStor/pump.sh','LocalManualConfig.py']
 for aarg in arg:
  z.append(aarg)
 msg={'req': 'LocalManualConfig', 'reply':z}
 ownerip=get('leader',owner)
 if ownerip[0]== -1:
  ownerip=get('known',owner)
  if ownerip[0]== -1:
   with open('/root/tmp','a') as f:
    f.write('ownerip is -1')
   return 3
 with open('/root/HostManualconfigtmp','w') as f:
  f.write('owner '+owner+"\n")
  f.write('ownerip '+ownerip[0][1]+"\n")
  f.write('msg '+str(msg)+"\n")
 sendhost(ownerip[0][1], str(msg),'recvreply',myhost)
 queuethis('HostManualconfig.py','stop',bargs[-1])
 return 1

if __name__=='__main__':
 setall(*sys.argv[1:])
