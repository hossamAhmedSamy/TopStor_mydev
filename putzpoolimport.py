#!/bin/python3.6
import subprocess
from etcdget import etcdget as get

def putzpoolimport():
 cmdline='/sbin/zpool import'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 sty=str(result)[2:][:-3].replace('\\t','').split('\\n')
 sty=get('activepool','--prefix')
 zdict={}
 zpool=[]
 for a in sty:
  zdict={ 'name':a[0].replace('activepool/',''), 'status':a[1]}
  zpool.append(zdict)
 print('pools',zpool)
 return zpool 

if __name__=='__main__':
 putzpoolimport()
