#!/bin/python3.6
import subprocess,sys
from logqueue import queuethis
from etcdput import etcdput as put
from broadcast import broadcast as broadcast 
from broadcasttolocal import broadcasttolocal as broadcasttolocal 
def send(*bargs):
	queuethis('HostManualconfigTZ.py','running',bargs[-1])
	put('tz',bargs[-1])
	broadcasttolocal('tz',bargs[-1])
	broadcast('HostManualConfigTZ','/TopStor/pump.sh','HostManualconfigTZ')
	queuethis('HostManualconfigTZ.py','stop',bargs[-1])
	return 1

if __name__=='__main__':
 send(*sys.argv[1:])
