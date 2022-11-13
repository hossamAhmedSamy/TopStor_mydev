#!/usr/bin/python3
import sys, logmsg, subprocess
from privthis import privthis 
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 

def volumeactive(pool,volname,prot,active,userreq):
 if privthis(prot,userreq) != 'true':
  print('not authorized user to do this task ')
  return
 logmsg.sendlog('Unmoutst01','info',userreq,volname,active)
 volinfo=get('volumes',volname)[0]
 if prot == 'CIFS':
  print('prot is',prot)
  activpos= maxpos = 9
 volright = volinfo[1].split('/')
 if len(volright) ==  maxpos:
  volright.append(active)
 else:
  volright[-1] = active
 ipaddr = volright[7]
 volright = '/'.join(volright)
 volleft = volinfo[0]
 cmdline='/TopStor/Volumeactivesh.sh '+pool+' '+volname+' '+prot+' '+active+' '+ipaddr+' '+userreq
 result = subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
 put(volleft,volright)
 logmsg.sendlog('Unmoutsu01','info',userreq,volname,active)
 return
 
if __name__=='__main__':
 volumeactive(*sys.argv[1:])
