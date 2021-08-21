#!/bin/python3.6
from etcdgetlocal import etcdget as get
from etcdputlocal import etcdput as put
from etcddellocal import etcddel as deli
from delbroadcastlocallocal import delbroadcastlocal as delilocal 
from broadcasttolocallocal import broadcasttolocal as broadtolocal 
import sys

def getipstatus(myip,ipaddr,vol):
 allvols=get(myip,'ipaddr/'+ipaddr)
 return allvols[0]

def clearvol(myip,vol):
 allvols=get(myip,'ipaddr','--prefix')
 volin=[x for x in allvols if vol in x[1] and '/' not in x[1].replace('/'+vol,'')]
 for x in volin:
  deli(myip,x[0],x[0])
  delilocal(myip,x[0],x[0])
 if len(volin) > 0:
  print('result='+volin[0][1].replace('/'+vol,''))
  return volin[0][1].replace('/'+vol,'')
 else:
  print('result=-1')
  return '-1' 

def redvol(myip,vol):
 allvols=get(myip,'ipaddr','--prefix')
 remvol=[(x[0],x[1].replace('/'+vol,'')) for x in allvols if vol in x[1] and '/' in x[1].replace('/'+vol,'')]
 for x in remvol:
  put(myip,x[0],x[1])
  broadtolocal(myip,x[0],x[1])
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
