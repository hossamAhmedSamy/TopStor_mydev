#!/usr/bin/python3
import subprocess,sys, datetime
from logqueue import queuethis
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
from broadcast import broadcast as broadcast 
from broadcasttolocal import broadcasttolocal as broadcasttolocal 
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost as sendhost
def send(*bargs):
	queuethis('HostManualconfigNTP.py','running',bargs[-1])
	if(len(bargs) < 1):
		args=bargs[0].split()
	else:
		args=bargs
	put('ntp',bargs[-1])
	broadcasttolocal('ntp',bargs[-1])
	broadcast('HostManualConfigNTP','/TopStor/pump.sh','HostManualconfigNTP')
	queuethis('HostManualconfigNTP.py','stop',bargs[-1])
	return 1

if __name__=='__main__':
 send(*sys.argv[1:])
