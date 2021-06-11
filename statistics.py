#!/bin/python3.6

from allphysicalinfo import getall 
from etcdgetpy import etcdget as get
vollisting = ['used', 'quota', 'usedbysnapshots' ]
def levelthis(fig,power='M'):
 leveldict = {'B':1, 'K':1024, 'M':1048576, 'G':1073741824, 'T':1099511627776}
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

def statsvol(voldict, limit=3):
 global vollisting
 statsdict = dict()
 for vollist in vollisting:
  pairing = []
  for vol in voldict:
   pairing.append([vol.split('_')[0], vol, voldict[vol][vollist]])
  pairing.sort(key=lambda x:x[2],reverse=True)
  finalpairing = []
  otherstats = 0
  count = -1
  for pair in pairing:
   count += 1
   if count < 3:
    finalpairing.append(pairing[count])
   else:
    otherstats += pairing[count][2]
  statsdict[vollist] = {'fulllabels':['others'], 'labels':['others'], 'stats':[otherstats] }
  for pair in finalpairing:
   statsdict[vollist]['fulllabels'].append(pair[1])
   statsdict[vollist]['labels'].append(pair[0])
   statsdict[vollist]['stats'].append(pair[2])
 return statsdict


def statsvol_all(voldict):
 global vollisting
 statsdict = dict()
 for vollist in vollisting:
  labels = []
  fulllabels = []
  stats = []
  for vol in voldict:
   labels.append(vol.split('_')[0])
   fulllabels.append(vol)
   stats.append(voldict[vol][vollist])
  statsdict[vollist] = {'fulllabels':list(fulllabels), 'labels':list(labels), 'stats':list(stats) }
 return statsdict 


def allvolstats(allinfo):
 vols = volumes(allinfo['volumes'])
 return statsvol(vols)
  

if __name__=='__main__':
 alldsks = get('host','current')
 allinfo = getall(alldsks)
 vols = volumes(allinfo['volumes'])
 statsvol(vols)
 
