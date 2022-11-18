#!/usr/bin/python3
import traceback, hashlib
import subprocess
from ast import literal_eval as mtuple
import time 

nowis = int(time.time())
nowfixed = str(nowis)[:4]
cmdline='/TopStor/grepthis.sh '+nowfixed+' /TopStordata/TopStorglobal.log'
result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
onedaylog = []
for res in result:
 if len(res.split()) < 4:
  continue
 if int(res.split()[-1]) > (nowis-3600):
  onedaylog.append(res)
print(onedaylog)
