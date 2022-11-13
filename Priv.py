#!/usr/bin/python3
import sys, subprocess
from etcdget import etcdget as get
from etcdput import etcdput as put
from socket import gethostname as hostname
from time import time as stamp
from broadcasttolocal import broadcasttolocal 
import logmsg

myhost=hostname()
def changepriv(user,priv,request='admin'):
 syspriv = 'UserPrivilegesch'
 cmdline = ['/TopStor/privthis.sh',syspriv, request]
 res = subprocess.run(cmdline,stdout=subprocess.PIPE).stdout
 if 'true' not in res.decode('utf-8'):
  return
 logmsg.sendlog('Priv1002 ','info',request,user)
 userinfo = get('usersinfo/'+user)
 leftpart = userinfo[0].split('/')[0:4]
 put('usersinfo/'+user, '/'.join(leftpart)+'/'+priv)
 put('user/'+myhost,str(stamp()))
 broadcasttolocal('usersinfo/'+user, '/'.join(leftpart)+'/'+priv)
 print('/'.join(leftpart)+'/'+priv)
 logmsg.sendlog('Priv1003','info',request,user)
 
 return


if __name__=='__main__':
 changepriv(*sys.argv[1:])

