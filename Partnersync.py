#!/usr/bin/python3
import sys, subprocess
from etcdput import etcdput as put
from etcdputlocal import etcdput as putlocal
from etcdget import etcdget as get 
from logqueue import queuethis
from PartnerAdd import addpartner as addpartner
from logmsg import sendlog
from socket import gethostname as hostname
from sendhost import sendhost
from privthis import privthis 
from time import time as timestamp
from broadcasttolocal import broadcasttolocal
myhost = hostname()
myip = get('ready/'+myhost)[0]
clusterip = get('namespace/mgmtip')[0].split('/')[0]
def partnersync(*bargs):
 partneralias = bargs[0]
 partnerinfo = get('Partner/'+partneralias)[0].split('/')
 partnerip = partnerinfo[0]
 replitype = partnerinfo[1]
 repliport = partnerinfo[2]
 phrase = partnerinfo[3]
 userreq = 'system'
 init = 'local'
 addpartner(partnerip, partneralias, replitype, repliport, phrase, userreq, init )
 

if __name__=='__main__':
 partnersync(*sys.argv[1:])
