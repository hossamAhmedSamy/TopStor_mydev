#!/bin/python3.6
import subprocess,sys, datetime
import json
from etcdget import etcdget as get
from etcdput import etcdput as put 
from broadcast import broadcast as broadcast 
from broadcasttolocal import broadcasttolocal as broadcasttolocal 
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost as sendhost
def send(*bargs):
	cmdline=['/TopStor/queuethis.sh','Diskrefresh.py','running',bargs[-1]]
	result=subprocess.run(cmdline,stdout=subprocess.PIPE)
	put('gw',bargs[-1])
	broadcasttolocal('gw',bargs[-1])
	broadcast('HostManualConfigTZ','/TopStor/pump.sh','Diskrefresh')
	cmdline=['/TopStor/queuethis.sh','DiskrefreshGW.py','finished',bargs[-1]]
	result=subprocess.run(cmdline,stdout=subprocess.PIPE)
	return 1

if __name__=='__main__':
 send(*sys.argv[1:])
