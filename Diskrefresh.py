#!/bin/python3.6
import subprocess,sys, datetime
from logqueue import queuethis
import json
from etcdget import etcdget as get
from etcdput import etcdput as put 
from broadcast import broadcast as broadcast 
from broadcasttolocal import broadcasttolocal as broadcasttolocal 
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost as sendhost
def send(*bargs):
	queuethis('Diskrefresh.py','running',bargs[-1])
	put('gw',bargs[-1])
	broadcasttolocal('gw',bargs[-1])
	broadcast('HostManualConfigTZ','/TopStor/pump.sh','Diskrefresh')
	queuethis('DiskrefreshGW.py','stop',bargs[-1])
	return 1

if __name__=='__main__':
 send(*sys.argv[1:])
