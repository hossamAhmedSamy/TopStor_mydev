#!/bin/sh
egrep 'etcdget|etcddel|etcdput'  * | egrep -v 'erase|Snapshot|SnapShot|Zpoolclrrun|Volume|Zpool|UpdateName|Unix|toonline|target|repli|Partner|Release|receivekeys|pumpkey|prot|riv|poolall|PartnerAdd|nfs|missing|log'
#grep 'hostname'
#grep 'broadcast' | grep -v '#' 
