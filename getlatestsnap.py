#!/bin/python3.6
from allphysicalinfo import getall 
import sys

def getlatestsnap(volume):
 allinfo = getall('0')
 allsnaps = allinfo['volumes'][volume]['snapshots']
 allsnaps.sort(key= lambda x: float(x.split('.')[1]), reverse=True)
 print ('latest','result_'+allsnaps[-1]+'result_')
 return allsnaps[-1]


if __name__=='__main__':
 getlatestsnap(*sys.argv[1:])
