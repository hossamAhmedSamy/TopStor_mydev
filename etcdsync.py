#!/bin/python3.6
import subprocess,sys
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from etcdputlocal import etcdputlocal as putlocal 
from etcddellocal import etcdellocal as dellocal 


thehost=sys.argv[1]
key=sys.argv[2]
tokey=sys.argv[3]
dellocal(key,'--prefix')
mylist=get(key,'--prefix')
if '-1' in mylist:
 print('-1')
 exit()
for item in mylist:
 putlocal(thehost, item[0], item[1]]
