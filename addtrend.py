#!/bin/python3.6
import sys
from etcdget import etcdget as get
from etcdput import etcdput as put
from broadcasttolocal import broadcasttolocal
from levelthis import levelthis


def addtrend(vol,size,stamp):
 normsize = str(levelthis(size))
 csizes = get('sizevol/'+vol)[0]
 csizes += '/'+stamp+'-'+normsize
 put('sizevol/'+vol,csizes)
 broadcasttolocal('sizevol/'+vol,csizes)
 
if __name__=='__main__':
 addtrend(*sys.argv[1:])
