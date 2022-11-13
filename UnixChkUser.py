#!/usr/bin/python3
import sys
from time import time as timestamp
from secrets import token_hex
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
import subprocess

def setlogin(leaderip,myhost, user,passw,token=0):
 if token == 0:
  oldpass = get(leaderip, 'usershash/'+user)[0].replace('\\n','')
  cmdline='/TopStor/decthis.sh '+user+' '+oldpass
  pass1=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode().split('_result')[1]
  if passw != pass1 and user=='admin':
   oldpass = str(get(leaderip, 'usershashadm/'+user)[0]).replace('\n','')
   cmdline='/TopStor/UnixChkUser '+user+' '+oldpass
   pass1=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode()
   if passw != pass1:
    return ({},0)
  token = token_hex(16)
 stamp = int(timestamp() + 3600)
 put(leaderip, 'login/'+user,token+'/'+str(stamp))
 userdict = {'user':user, 'timestamp':stamp}
 print(userdict,token)
 return (userdict, token)
 

if __name__=='__main__':
 setlogin(*sys.argv[1:])
