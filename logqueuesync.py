#!/bin/python3.6
import sys, subprocess,os
from etcdget import etcdget as get
from etcdput import etcdput as put 
from etcddel import etcddel as dels 
from socket import gethostname as hostname
from sendhost import sendhost
def syncnextlead(lastfile):
 filelist = os.listdir('/TopStordata/')
 filelist = [ x for x in filelist if 'taskperf' in x ]
 filelist.sort()
 filetosend = [ x for x in filelist if filelist.index(x) > filelist.index(lastfile) ]
 print(filetosend)
 
 return  
 
 
if __name__=='__main__':
 syncnextlead('taskperf-2021041522')
