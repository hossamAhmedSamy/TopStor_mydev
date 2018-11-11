#!/bin/python3.6
import subprocess,sys
from etcdget import etcdget as get
from threading import Thread
from etcdgetlocal import etcdget as getlocal
from ast import literal_eval as mtuple
from socket import gethostname as hostname
def thread_add(user):
 username=user[0].replace('usersinfo/','')
 userinfo=user[1].split(':')
 userid=userinfo[0]
 usergd=userinfo[1]
 userhash=get('usershash/'+username)[0]
 userhome=userinfo[2]
 cmdline=['/TopStor/UnixAddUser_sync',username,userhash,userid,usergd,userhome]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
def thread_del(user):
 username=user[0].replace('usersinfo/','')
 if username not in str(allusers):
 cmdline=['/TopStor/UnixDelUser_sync',username,'system']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)

def usersyncall(*args):
 threads=[]
 allusers=get('usersinfo','--prefix')
 myusers=getlocal(args[0],'usersinfo','--prefix')
 for user in allusers:
  x=Thread(target=thread_add,name='addingusers',args=user)
  x.start()
  threads.append(x) 
 for user in myusers:
  x=Thread(target=thread_del,name='deletingusers',args=user)
  x.start()
  threads.append(x) 
 for tt in threads:
  tt.join()
   
  
if __name__=='__main__':
 usersyncall(*sys.argv[1:])
