#!/bin/python3.6
import sys
from etcdget import etcdget as get
from etcdput import etcdput as put
from broadcasttolocal import broadcasttolocal 
def changepriv(user,priv):
 userinfo = get('usersinfo/'+user)
 leftpart = userinfo[0].split('/')[0:4]
 put('usersinfo/'+user, '/'.join(leftpart)+'/'+priv)
 broadcasttolocal('usersinfo/'+user, '/'.join(leftpart)+'/'+priv)
 print('/'.join(leftpart)+'/'+priv)
 
 return


if __name__=='__main__':
 changepriv(*sys.argv[1:])

