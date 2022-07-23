#!/bin/python3.6
import sys
from time import time as timestamp, sleep
from allphysicalinfo import getall 
from etcdgetpy import etcdget as get
from getallraids import newraids, selectdisks

allinfo = {}

def repliparam(snapshot):
 volume = snapshot.split('/')[1].split('@')[0]
 snapshot = snapshot.split('@')[1]
 volused = allinfo['volumes'][volume]['referenced'] 
 snapused = '0' 
 print('result_'+volume, volused, snapshot+'result_') 
 return 'result_'+volume, volused, snapshot+'result_'



if __name__=='__main__':
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 result = repliparam(*sys.argv[1:])
   
  
# disks = allinfo['disks']
# raids = newraids(disks)
# print(raids)
 
