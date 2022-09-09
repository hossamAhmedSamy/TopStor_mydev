#!/bin/python3.6
import sys

def levelthis(fig,power='G'):
 leveldict = {'B':1, 'K':1024, 'M':1048576, 'G':1073741824,'T':1099511627776}
 level = str(fig).replace(',','').upper().replace('MB','M').replace('GB','G').replace('KB','K').replace('TB','T')

 if level[-1] in leveldict:
  try:
   num = float("".join(level[:-1]))*leveldict[level[-1]]/leveldict[power]
  except:
   num = 0
 else:
  try:
   num = float(level)/leveldict[power]
  except:
   num = 0.0 
 return num 

if __name__=='__main__':
 num = levelthis(*sys.argv[1:]) 
 print(num)
