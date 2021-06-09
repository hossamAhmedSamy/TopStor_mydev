#!/bin/python3.6

from allphysicalinfo import getall 
from etcdget import etcdget as get
vollisting = ['used', 'quota', 'usedbysnapshots' ]
def levelthis(fig,power='M'):
 leveldict = {'B':1, 'K':1024, 'M':1048576, 'G':1073741824}
 figure = str(fig).replace(',','')
 level = figure[-1].upper()
 if level in leveldict:
  num = float(figure[:-1])*leveldict[level]/leveldict[power]
 else:
   num = float(figure)/leveldict[power]
 return num 

def volumes(voldict):
 global vollisting
 for vol in voldict:
  for vollist in vollisting:
   voldict[vol][vollist] = levelthis(voldict[vol][vollist])
 return voldict

def statsvol(voldict):
 global vollisting
 statsdict = dict()
 for vollist in vollisting:
  labels = []
  stats = []
  for vol in voldict:
   labels.append(vol)
   stats.append(voldict[vol][vollist])
  statsdict[vollist] = {'labels':list(labels), 'stats':list(stats) }
 return statsdict 


def allvolstats(allinfo):
 print('allinf',allinfo)
 vols = volumes(allinfo['volumes'])
 return statsvol(vols)
  

if __name__=='__main__':
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 vols = volumes(allinfo['volumes'])
 statsvol(vols)
 
