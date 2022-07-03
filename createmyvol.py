#!/bin/python3.6
import sys
from etcdgetpy import etcdget as get

def createvol(*args)
 datastr = ''
 owner = args[1] 
 ownerip = get('ready/'+args[1])[0]
 pool = args[2]
 name = args[3]
 ipaddress = args[4]
 Subnet = args[5]
 user = 'system'
 typep = args[6]
 if 'ISCSI' in typep:
  chapuser = 'MoatazNegm'
  chappas = 'MezoAdmin'
  portalport = args[7]
  initiators = args[8]
  datastr = pool+' '+name+' '+size+' '+ipaddress+' '+Subnet+' '+portalport+' '+initiators+' '+chapuse+' '+chappas+' '+user+' '+owner+' '+user
 elif 'CIFSdom' in typep:
  domname = args[7]
  dompass = args[8]
  domsrv = args[9]
  domip = args[10]
  domadmin = args[11]
  cmdline=['./encthis.sh',dompass]
  dompass=subprocess.run(cmdline,stdout=subprocess.PIPE).stdout.decode().replace('/','@@sep')[:-1]
  datastr = pool+' '+name+' '+size+' '+ipaddress+' '+Subnet+' '+user+' '+owner+' '+user+' '+domname+' '+domsrv+' '+ domip+' '+domadmin+' '+dompass 
 else:
  groups = args[7]
  datastr = pool+' '+name+' '+size+' '+groups+' '+ipaddress+' '+Subnet+' '+user+' '+owner+' '+user
 print('#############################')
 print(data)
 print(datastr)
 print('###########################')
 cmndstring = '/TopStor/pump.sh VolumeCreate'+typep+' '+datastr
 result=subprocess.run(cmndstring,stdout=subprocess.PIPE)
 return 


if __name__=='__main__':

 createvol(*sys.argv[1:])

