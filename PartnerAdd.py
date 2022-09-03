#!/bin/python3.6
import sys, subprocess
from etcdput import etcdput as put
from etcdputlocal import etcdput as putlocal
from etcdget import etcdget as get 
from etcddel import etcddel as dels 
from logqueue import queuethis
from logmsg import sendlog
from socket import gethostname as hostname
from sendhost import sendhost
from privthis import privthis 
from time import time as stamp
from broadcasttolocal import broadcasttolocal


def dosync(leader,*args):
  put(*args)
  put(args[0]+'/'+leader,args[1])
  return 


myhost = hostname()
myip = get('ready/'+myhost)[0]
clusterip = get('namespace/mgmtip')[0].split('/')[0]
def addpartner(*bargs):
 with open('/root/PartnerAdd','w') as f:
  f.write(str(bargs))
 partnerip = bargs[0]
 partneralias = bargs[1].replace('_','').replace('/',':::')
 replitype = bargs[2]
 repliport = bargs[3]
 phrase = bargs[4]
 userreq = bargs[5]
 init = bargs[6]
 if (privthis('Replication',userreq) != 'true'):
  print('not authorized to add partner')
  return
 sendlog('Partner1000','info',userreq,partneralias,replitype)
 if 'Sender' not in replitype:
  cmdline = '/TopStor/preparekeys.sh '+partnerip
  result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')[0].replace(' ','_spc_')
  z=['/TopStor/pump.sh','receivekeys.sh',myhost,myip,clusterip, replitype, repliport, phrase, result]
  msg={'req': 'Exchange', 'reply':z}
  print(msg)
  sendhost(partnerip, str(msg),'recvreply',myhost)
  cmdline = '/TopStor/checkpartner.sh '+partneralias+' '+replitype+' '+partnerip+' '+repliport+' '+clusterip+' '+phrase+' '+'new'
  print('sending',cmdline.split())
  result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
  if 'open' not in result:
   sendlog('Partner1fa2','error',userreq,partneralias,replitype)
   return
# broadcasttolocal('Partner/'+partneralias+'_'+replitype,partnerip+'/'+replitype+'/'+str(repliport)+'/'+phrase) 
 if 'init' in init:
  #dels('Partner/'+partneralias+'_'+replitype, '--prefix')
  #dosync(myhost,'sync/Partnr/Del_'+partneralias+':::'+replitype+'_--prefix/request','PartnerDel_'+str(stamp))
  put('Partner/'+partneralias+'_'+replitype , partnerip+'/'+replitype+'/'+str(repliport)+'/'+phrase) 
  dosync(myhost,'sync/Partnr/Add_'+partneralias+':::'+replitype+'_'+partnerip+'::'+replitype+'::'+str(repliport)+'::'+phrase+'/request','Partnr_str_'+str(stamp())) 
# else:
#  putlocal(myip,'Partner/'+partneralias+'_'+replitype,partnerip+'/'+replitype+'/'+str(repliport)+'/'+phrase) 

 sendlog('Partner1002','info',userreq,partneralias,replitype)
 

if __name__=='__main__':
 addpartner(*sys.argv[1:])
