#!/bin/python3.6
import subprocess
from etcdgetpy import etcdget as get

def putzpoolimport():
 sty=get('activepool','--prefix')
 zdict={}
 zpool=[]
 for a in sty:
  zdict={ 'name':a[0].replace('activepool/',''), 'status':a[1]}
  zpool.append(zdict)
 print('pools',zpool)
 return zpool 

def listpools():
 pooldict = {}
 readyhosts = get('ready','--prefix')
 founds = get('poolfound','--prefix')
 locks = get('poollock','--prefix')
 readies = get('poolready','--prefix')
 deleted = get('pooldeleted','--prefix')
 for found in founds:
  poolname = found[0].replace('poolfound/','') 
  if poolname not in str(readies) and poolname not in str(deleted) and found[1] in str(readyhosts) and poolname not in str(locks):
   if poolname not in pooldict:
    pooldict[poolname] = []
   pooldict[poolname].append(found[1])
 print(pooldict)
 return pooldict

if __name__=='__main__':
 #putzpoolimport()
 listpools()

