#!/usr/bin/python3
import subprocess,sys, os
import json
from time import sleep

os.environ['ETCDCTL_API']= '3'

def etcdgetjson(etcd, key,prefix=''):
 cmdline=['etcdctl','--endpoints=http://'+etcd+':2379','get',key,prefix]
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 try:
  if len(prefix) > 0: 
   mylist=str(result.stdout.decode()).replace('\n\n','\n').split('\n')
   mylist=zip(mylist[0::2],mylist[1::2])
   hostid=0
   hosts=[]
   for x in mylist:
    ll=[]
    #xx=str(x[1]).replace('{','{"').replace('}','"}').replace(':','":"').repalce(',','","')
    xx=x[1]
    ll.append(xx)
    hostsdic={'id':str(hostid),'name':x[0],'prop':xx}
    hostid=hostid+1
    hosts.append(hostsdic)
    if 'prefix' not in prefix:
     hosts=[x for x in hosts if prefix in str(x)]
   #return str(hosts).replace('"','').replace("'",'"')
   #print(hosts)
   print(hosts)
   return hosts
   
  else:
   #print(dict(str(result.stdout).split(key)[1][2:][:-3].replace("'",'"')))
   res =  dict(str(result.stdout).split(key)[1][2:][:-3].replace("'",'"'))
   print(res)
   return dict(str(result.stdout).split(key)[1][2:][:-3].replace("'",'"'))
 
 except:
  print(dict([{'result':'_1'}]))
  return dict([{'result':'_1'}]) 

if __name__=='__main__':
 etcdgetjson(*sys.argv[1:])
