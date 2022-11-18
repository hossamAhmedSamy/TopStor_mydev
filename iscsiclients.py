#!/usr/bin/python3
import subprocess
from ast import literal_eval as mtuple
import socket
from os import listdir
from os.path import isfile, join

cmdline=['/pace/etcdgetlocal.py','known','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
clients=str(result.stdout).replace('known/','')[2:][:-3].split('\\n')
cmdline=['/pace/etcdgetlocal.py','leader','--prefix']
result=subprocess.run(cmdline,stdout=subprocess.PIPE)
clients+=str(result.stdout).replace('leader/','')[2:][:-3].split('\\n')
client=[]
for c in clients:
 try:
  c=mtuple(c)
  print(c[0])
 except:
  pass
