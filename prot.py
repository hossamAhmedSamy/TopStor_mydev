#!/bin/python3.6
from etcdget import etcdget as get
from etcdput import etcdput as put
from etcddel import etcddel as deli
from delbroadcastlocal import delbroadcastlocal as delilocal 
from time import time as stamp
from broadcasttolocal import broadcasttolocal as broadtolocal 
from socket import gethostname as hostname
import sys
myhost=hostname()
def getipstatus(ipaddr,ipsubnet,vol):
 allvols=get('ipaddr/'+ipaddr+'/'+ipsubnet)
 return allvols[0]

def clearvol(vol):
 allvols=get('ipaddr','--prefix')
 volin=[x for x in allvols if vol in x[1] and '/' not in x[1].replace('/'+vol,'')]
 for x in volin:
  deli(x[0],x[0])
  delilocal(x[0],x[0])
 put('sync/ipaddr/'+myhost,str(stamp()))
 if len(volin) > 0:
  print('result='+volin[0][1].replace('/'+vol,''))
  return volin[0][1].replace('/'+vol,'')
 else:
  print('result=-1')
  return '-1' 

def redvol(vol):
 allvols=get('ipaddr','--prefix')
 remvol=[(x[0],x[1].replace('/'+vol,'')) for x in allvols if vol in x[1] and '/' in x[1].replace('/'+vol,'')]
 for x in remvol:
  put(x[0],x[1])
  broadtolocal(x[0],x[1])
 put('sync/ipaddr/'+myhost,str(stamp()))
 if len(remvol) > 0:
  print('result='+remvol[0][1].split('/')[0])
  return 'result='+remvol[0][1].split('/')[0]
 else:
  print('result=-1')
  return 'result=-1' 

if __name__=='__main__':
# getipstatus(*sys.argv[1:])
 func={}
 func['getipstatus']=getipstatus
 func['clearvol']=clearvol
 func['redvol']=redvol
 func[sys.argv[1]](*sys.argv[2:])
