#!/bin/python3.6
from etcddel import etcddel as etcddel
from etcdput import etcdput as put 
from etcdget import etcdget as get 
import socket, sys, subprocess

def addhost(*args):
 myhost=socket.gethostname()
 allready=get('ready','--prefix')
 with open('/TopStor/grafana.files/hosts','w') as fw:
  with open('/TopStor/grafana.files/hosts.orig','r') as fr:
   with open('/TopStor/prometheus.files/hosts','w') as pfw:
    with open('/TopStor/prometheus.files/hosts.orig','r') as pfr:
     with open('/TopStor/prometheus.files/prometheus.yml','w') as ppfw:
      with open('/TopStor/prometheus.files/prometheus.yml.orig','r') as ppfr:
       fw.write(fr.read())
       pfw.write(pfr.read())
       ppfw.write(ppfr.read())
       for ready in allready:
        fw.write('\n'+ready[1]+' '+ready[0].replace('ready/',''))
        pfw.write('\n'+ready[1]+' '+ready[0].replace('ready/',''))
        ppfw.write("       - '"+ready[0].replace('ready/','')+":9090'"+'\n')
 cmdline=['/bin/docker','restart','prom']
 subprocess.run(cmdline,stdout=subprocess.PIPE)
 cmdline=['/bin/docker','restart','grafana']
 subprocess.run(cmdline,stdout=subprocess.PIPE)
  
 return
if __name__=='__main__':
 addhost(*sys.argv[1:])
