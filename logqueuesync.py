#!/usr/bin/python3
import sys
def syncnextlead(lastfile):
 filelist = os.listdir('/TopStordata/')
 filelist = [ x for x in filelist if 'taskperf' in x ]
 filelist.sort()
 filetosend = [ x for x in filelist if filelist.index(x) > filelist.index(lastfile) ]
 print(filetosend)
 
 return  
 
 
if __name__=='__main__':
 syncnextlead('taskperf-2021041522')
