#!/usr/bin/python3
import sys
from broadcast import broadcast as broadcast 
def send(*bargs):
	broadcast('HostgetIPs','/TopStor/pump.sh','HostgetIPs',bargs[0])
	return 1

if __name__=='__main__':
 send(*sys.argv[1:])
