#!/usr/bin/python3
import sys
from time import time as timestamp
from secrets import token_hex
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
import subprocess

def setlogin(leaderip, user,passw,token=0):
 if token == 0:
  cmdline='/TopStor/UnixChkUser '+user+' '+passw
  pass1=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8')
  oldpass = str(get(leaderip, 'usershash/'+user)[0])
  if oldpass not in pass1:
   oldpass = str(get(leaderip, 'usershashadm/'+user)[0])
   if oldpass not in pass1:
    return ({},0)
  token = token_hex(16)
 stamp = int(timestamp() + 3600)
 put(leaderip, 'login/'+user,token+'/'+str(stamp))
 userdict = {'user':user, 'timestamp':stamp}
 return (userdict, token)
 

if __name__=='__main__':
 setlogin(*sys.argv[1:])
