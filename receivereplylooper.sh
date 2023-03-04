#!/usr/bin/sh
fnloop () {
cd /TopStor
/TopStor/topstorrecvreply.py
}
while true;
do
 fnloop 
 sleep 1 
done

