#!/bin/python3.6
import sys
from etcdput import etcdput as put
from logqueue import queuethis
from logmsg import sendlog
from privthis import privthis 
from broadcasttolocal import broadcasttolocal

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
 sendlog('Partner1007','info',userreq,partneralias)
 broadcasttolocal('Partner/'+partneralias,partnerip+'/'+replitype+'/'+str(repliport)+'/'+phrase) 
 put('Partner/'+partneralias,partnerip+'/'+replitype+'/'+str(repliport)+'/'+phrase) 
 sendlog('Partner1009','info',userreq,partneralias,replitype)
 

if __name__=='__main__':
 addpartner(*sys.argv[1:])
