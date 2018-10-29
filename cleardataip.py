#!/bin/python3.6
import subprocess,sys
from etcdget import etcdget as get
import json
def cleardataip(*args):
	nslist=get('dataip','--prefix')
	for x in nslist:
		name=x[0].replace('/','')
		params=x[1].split('/')
		cmdline='/sbin/ip addr del '+params[0]+'/'+params[1]+' dev '+params[2] 
		subprocess.run(cmdline.split(),stdout=subprocess.PIPE)

if __name__=='__main__':
 cleardataip(*sys.argv[1:])
