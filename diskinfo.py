import sys
import json


data=json.load(open(sys.argv[1]));
for x in data:
  if x["name"]==sys.argv[2]:
   print(x["id"])
