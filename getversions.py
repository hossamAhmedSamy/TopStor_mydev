#!/usr/bin/python3

import subprocess

def getversions():
 cmdline='git branch'
 versions = []
 verdict = dict()
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout
 id = 0
 for res in result.decode('utf-8').split('\n'):
  if 'QS' in res:
   if '*' in res:
    cversion = res.split('QS')[1]
   versions.append({'id': id, 'text':res.split('QS')[1]})
   id += 1
 verdict = { 'versions': versions, 'current': cversion } 
 return verdict 

if __name__=='__main__':
 getversions()
