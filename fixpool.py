#!/usr/bin/python3
from etcdgetlocalpy import etcdget as get
import subprocess, socket

myhost=socket.gethostname()
pools=get('fixpool','--prefix')
for p in pools:
 pool=p[0].replace('fixpool/','')
 host=get('pools/'+pool)[0]
 if myhost==host:
  cmdline='/TopStor/fixpool.sh '+pool
  result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE)
