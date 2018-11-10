#!/bin/python3.6
import subprocess,sys
from etcdget import etcdget as get
from ast import literal_eval as mtuple
from etcdputlocal import etcdput as putlocal 
from etcddellocal import etcddel as dellocal 


thehost=sys.argv[1]
key=sys.argv[2]
tokey=sys.argv[3]
print('thehost',thehost,tokey)
slash=1
mylist=get(key+'/','--prefix')
if len(mylist) == 0:
 mylist=get(key,'--prefix')
 slash=0
if slash==0:
 dellocal(thehost,tokey,'--prefix')
else:
 dellocal(thehost,tokey+'/','--prefix')

print('mylist:',mylist)
if '-1' in mylist:
 print('-1')
 exit()
for item in mylist:
 if slash==1:
  putlocal(thehost, tokey+'/'+item[0].split('/')[1], item[1])
 else:
  putlocal(thehost, tokey,item[1])
 
