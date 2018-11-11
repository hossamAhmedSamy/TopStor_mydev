#!/bin/python3.6
import subprocess,sys
import json

def etcdget(thehost,key, prefix=''):
 endpoints=''
 endpoints='http://'+thehost+':2378'
 cmdline=['etcdctl','--endpoints='+endpoints,'get',key,prefix]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 if(result.stdout==b''):
   print('-1')
   exit(1)
 try:
  if(prefix !=''):
   mylist=str(result.stdout)[2:][:-3].split('\\n')
   zipped=zip(mylist[0::2],mylist[1::2])
   for x in zipped:
    print(x)
  else:
   if(result==['']):
    print('-1')
   print(str(result.stdout).split(key)[1][2:][:-3])
  
 except:
  print('-1')

if __name__=='__main__':
 etcdget(*sys.argv[1:])
