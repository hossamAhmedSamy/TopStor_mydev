#!/bin/python3.6
from broadcast import broadcast as broadcast 
def send(*bargs):
	broadcast('HostgetIPs','/TopStor/pump.sh','HostgetIPs')
	return 1

if __name__=='__main__':
 send(*sys.argv[1:])
