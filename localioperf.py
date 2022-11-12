#!/usr/bin/python3
import subprocess, sys

def ioperf():

 cmdline='iostat -k'
 result=subprocess.run(cmdline.split(),stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
 diskres = result[6:]
 print(diskres)
if __name__=='__main__':
 ioperf(*sys.argv[1:])
