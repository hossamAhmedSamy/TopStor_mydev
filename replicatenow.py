#!/bin/python3.6
import sys
from time import time as timestamp, sleep
from allphysicalinfo import getall 
from etcdgetpy import etcdget as get
from getallraids import newraids, selectdisks

allinfo = {}
def replitargetget(receiver, volume, volused, snapshot):
 partnerinfo = get('Partner/'+receiver)
 print(type(partnerinfo), partnerinfo)

def repliparam(snapshot, receiver):
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 volume = snapshot.split('/')[1].split('@')[0]
 snapshot = snapshot.split('@')[1]
 volused = allinfo['volumes'][volume]['referenced'] 
 snapused = '0' 
 replitargetget(receiver, volume, volused, snapshot)
 return 'result_'+volume, volused, snapshot+'result_'



if __name__=='__main__':
 result = repliparam(*sys.argv[1:])
   
  
# disks = allinfo['disks']
# raids = newraids(disks)
# print(raids)
 
