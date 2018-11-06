#!/bin/python3.6
import sys
from ast import literal_eval as mtuple

def importpools(*args):
 with open('/TopStordata/forlocalpools') as f:
  for line in f:
   pool=mtuple(line)[0].split('/')[1]
     cmdline=['/TopStor/Zpool2 import -c /TopStordata/'+pool+' -am']
     result=subprocess.run(cmdline,stdout=subprocess.PIPE)
   print(pool)
 return

if __name__ == "__main__":
 importpools(*sys.argv[1:])
 
