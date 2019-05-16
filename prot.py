#!/bin/python3.6
from etcdget import etcdget as get
from etcdput import etcdput as put
from etcddel import etcddel as deli
from delbroadcastlocal import delbroadcastlocal as delilocal 
from broadcasttolocal import broadcasttolocal as broadtolocal 
import sys

def getipstatus(ipaddr,vol):
 allvols=get('ipaddr/'+ipaddr)
 return allvols[0]

def clearvol(vol):
 allvols=get('ipaddr','--prefix')
 volin=[x for x in allvols if vol in x[1] and '/' not in x[1].replace('/'+vol,'')]
 remvol=[(x[0],x[1].replace('/'+vol,'') for x in allvols if vol in x[1] and '/' in x[1].replace('/'+vol,'')]
 for x in remvol:
  put(x[0],x[1])
  broadtolocal(x[0],x[1])
 for x in volin:
  deli(x[0],x[0])
  delilocal(x[0],x[0])
 if len(volin) > 0:
  return volin[0][1].replace('/'+vol,'')
 else:
  return '-1' 

if __name__=='__main__':
# getipstatus(*sys.argv[1:])
 func={}
 func['getipstatus']=getipstatus
 func['clearvol']=clearvol
 func[sys.argv[1]](*sys.argv[2:])
