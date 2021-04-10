#!/bin/python3.6
import subprocess,sys, datetime
from logqueue import queuethis
from etcdput import etcdput as put 
import logmsg
def do(*args):
 with open('/pacedata/perfmon','r') as f:
  perfmon = f.readline()
 if '1' in perfmon:
  queuethis('Evacuate','toremove',args[-1])
 logmsg.sendlog('Evacuaest01','info',args[-1],args[-2])
 put('toremove/'+args[-2],'start')
 put("tosync","yes")

if __name__=='__main__':
 do(*sys.argv[1:])
