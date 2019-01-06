#!/bin/python3.6
import subprocess

def putzpoolimport():
 cmdline='/sbin/zpool import'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 sty=str(result)[2:][:-3].replace('\\t','').split('\\n')
 zdict={}
 zpool=[]
 for a in sty:
  print('aaaaaa',a)
  b=a.split()
  if len(b) > 1:
   if "pdhc" in b[0] and  'pool:' not in str(b):
    #if 'DEG' in b[1] or 'ONLI' in b[1]:
     zdict={ 'name':b[0], 'status':b[1]}
     zpool.append(zdict)
 print('pools',zpool)
 return zpool 

if __name__=='__main__':
 putzpoolimport()
