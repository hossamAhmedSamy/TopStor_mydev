#!/usr/bin/python3
import sys, subprocess
from etcdput import etcdput as put
from etcdgetlocal import etcdget as get 
from logqueue import queuethis
from logmsg import sendlog
from sendhost import sendhost
from privthis import privthis 
from time import time as stamp


myhost = get('clusternode')[0] 
myip = get('clusternodeip')[0]
clusterip = get('leaderip')[0]

def dosync(leader,*args):
  global leaderip
  put(leaderip, *args)
  put(leaderip, args[0]+'/'+leader,args[1])
  return 


def addpartner(*bargs):
 global leaderip, myhost, myip
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
  put(leaderip, 'Partner/'+partneralias+'_'+replitype , partnerip+'/'+replitype+'/'+str(repliport)+'/'+phrase) 
  dosync(myhost,'sync/Partnr/Add_'+partneralias+':::'+replitype+'_'+partnerip+'::'+replitype+'::'+str(repliport)+'::'+phrase+'/request','Partnr_str_'+str(stamp())) 

 sendlog('Partner1002','info',userreq,partneralias,replitype)
 

if __name__=='__main__':
 addpartner(*sys.argv[1:])
