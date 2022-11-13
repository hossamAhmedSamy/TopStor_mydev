#!/usr/bin/python3
import sys
from time import time as timestamp
from secrets import token_hex
from etcdgetpy import etcdget as get
from etcdput import etcdput as put 
import subprocess

def setlogin(leaderip, myhost, user,passw,tokenbase=0):
 token=-1
 cmdline='/TopStor/encthis.sh '+user+' '+passw
 pass1=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('_result')[1]
 put(leaderip, 'usershash/'+user,pass1)
 put(leaderip, 'usershashadm/'+user,pass1)
 sett=get(leaderip, 'usershash','--prefix')
 print('sett',sett)
 

if __name__=='__main__':
 setlogin(*sys.argv[1:])
