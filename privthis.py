#!/usr/bin/python3
import subprocess,sys, datetime
from logqueue import queuethis
import json
from etcdgetpy import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def privthis(*bargs):
 etcd = bargs[0]
 priv = bargs[1] 
 userreq = bargs[2]
 if userreq in ['admin','system']:
  return 'true' 
 userpriv = get(etcd, 'usersinfo/'+userreq)
 if priv in str(userpriv) and str(userpriv) != '-1':
   return userpriv[0].split(priv+'-')[1].split('/')[0]
 else:
  return 'False'

if __name__=='__main__':
 privthis(*sys.argv[1:])
