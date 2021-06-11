#!/bin/python3.6
import subprocess,sys, os
import json
def takesnap(*args):
 os.environ['ETCDCTL_API']= '3'
 endpoints=''
 data=json.load(open('/pacedata/runningetcdnodes.txt'));
 for x in data['members']:
  endpoints=endpoints+str(x['clientURLs'])[2:][:-2]+','
 cmdline=['/bin/etcdctl','snapshot','save', '--endpoints='+endpoints,'/TopStordata/etcdsnap.bak']
 result=subprocess.run(cmdline,stdout=subprocess.PIPE)
 print(result)


if __name__=='__main__':
 takesnap(*sys.argv[1:])
