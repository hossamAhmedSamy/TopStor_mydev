#!/usr/bin/python3
import subprocess,sys, datetime
from logqueue import queuethis
import json
from etcdgetpy import etcdget as get
from ast import literal_eval as mtuple
from socket import gethostname as hostname
from sendhost import sendhost
def privthis(*bargs):
 priv = bargs[0] 
 userreq = bargs[1]
 if userreq in ['admin','system']:
  return 'true' 
 userpriv = get('usersinfo/'+userreq)
 if priv in str(userpriv):
   return userpriv[0].split(priv+'-')[1].split('/')[0]
 else:
  return False

if __name__=='__main__':
 privthis(*sys.argv[1:])
