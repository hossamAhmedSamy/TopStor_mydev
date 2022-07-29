#!/bin/python3.6
from allphysicalinfo import getall 
import sys

def getlatestsnap(volume):
 allinfo = getall('0')
 allsnaps = allinfo['volumes'][volume]['snapshots']
 allsnaps = sorted(allsnaps,key= lambda x: float(x.split('.')[1]))
 print ('latest',allsnaps[0])



if __name__=='__main__':
 getlatestsnap(*sys.argv[1:])
