#!/usr/bin/python3
import sys, subprocess
from etcdget import etcdget as get
from etcdput import etcdput as put
from time import time as stamp
import logmsg

def dosync(leader, leaderip, sync, *args):
  global leaderip, leader
  dels(leaderip, sync)
  put(leaderip, *args)
  put(leaderip, args[0]+'/'+leader,args[1])
  return 


def changepriv(leader, leaderip, myhost, myip, user,priv,request='admin'):
 logmsg.initlog(leaderip,myhost)
 if leader == myhost:
    etcdip = leaderip
 else:
    etcdip = myip
 syspriv = 'UserPrivilegesch'
 cmdline = ['/TopStor/privthis.sh',syspriv, request]
 res = subprocess.run(cmdline,stdout=subprocess.PIPE).stdout
 if 'true' not in res.decode('utf-8'):
  return
 logmsg.sendlog('Priv1002 ','info',request,user)
 userinfo = get(etcdip,'usersinfo/'+user)
 leftpart = userinfo[0].split('/')[0:4]
 put(leaderip, 'usersinfo/'+user, '/'.join(leftpart)+'/'+priv)
 dosync(leader, leaderip, 'sync/priv/'+user,'sync/priv/'+user, 'priv_'+str(stamp()))
 #put(leaderip, 'user/'+myhost,str(stamp()))
 #broadcasttolocal('usersinfo/'+user, '/'.join(leftpart)+'/'+priv)
 print('/'.join(leftpart)+'/'+priv)
 logmsg.sendlog('Priv1003','info',request,user)
 
 return


if __name__=='__main__':
 changepriv(*sys.argv[1:])

