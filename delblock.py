#!/bin/python3.6
import subprocess,sys
import json
def delblock(start,stop,filename):
 x=""
 flag=0
 with open(filename,'r') as f:
  for line in f:
   if start in line:
    flag=1
   elif stop in line:
    flag=0
   elif flag==0:
    x=x+line 
 with open(filename+'.new','w') as f:
  f.write(x)
 return 
if __name__=='__main__':
 delblock(*sys.argv[1:])
