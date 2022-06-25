#!/bin/python3.6
import sys, subprocess
from etcdput import etcdput as put
from etcdget import etcdget as get 
from logqueue import queuethis
from logmsg import sendlog
from socket import gethostname as hostname
from sendhost import sendhost
from privthis import privthis 
from broadcasttolocal import broadcasttolocal
myhost = hostname()
myip = get('ready/'+myhost)[0]
clusterip = get('namespace/mgmtip')[0].split('/')[0]
def addpartner(*bargs):
 partnerip = bargs[0]
 partneralias = bargs[1]
 replitype = bargs[2]
 repliport = bargs[3]
 phrase = bargs[4]
 userreq = bargs[5]
 if (privthis('Replication',userreq) != 'true'):
  print('not authorized to add partner')
  return
 sendlog('Partner1000','info',userreq,partneralias,replitype)
 cmdline = '/TopStor/preparekeys.sh '+partnerip
 result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')[0]
 z=['/TopStor/pump.sh','receivekeys.sh',myhost,myip,clusterip, repliport, replitype, phrase, result]
 msg={'req': 'Exchange', 'reply':z}
 print(msg)
 sendhost(partnerip, str(msg),'recvreply',myhost)
 return
 broadcasttolocal('Partner/'+partneralias,partnerip+'/'+replitype+'/'+str(repliport)+'/'+phrase) 
 put('Partner/'+partneralias,partnerip+'/'+replitype+'/'+str(repliport)+'/'+phrase) 
 sendlog('Partner1002','info',userreq,partneralias,replitype)
 

if __name__=='__main__':
 addpartner(*sys.argv[1:])
