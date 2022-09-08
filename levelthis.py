#!/bin/python3.6
import sys

def levelthis(fig,power='G'):
 leveldict = {'B':1, 'K':1024, 'M':1048576, 'G':1073741824,'T':1099511627776}
 if fig == None or fig == '':
  fig = 0
 level = str(fig).replace(',','').upper().replace('MB','M').replace('GB','G').replace('KB','K').replace('TB','T')
 if level == None:
  level = '0'
 print('#################333')
 print(level)
 print('#################333')

 if level[-1] in leveldict:
  num = float(level[:-1])*leveldict[level[-1]]/leveldict[power]
 else:
   num = float(level)/leveldict[power]
 return num 

if __name__=='__main__':
 num = levelthis(*sys.argv[1:]) 
 print(num)
