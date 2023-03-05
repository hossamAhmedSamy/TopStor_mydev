#!/usr/bin/sh
fnkillall () {
process=(`ps -ef | grep $1 | grep -v color | grep -v grep | awk '{print $2}'`)
for proc in "${process[@]}"; do
 echo proc $proc
 kill -9 $proc 2>/dev/null
done
}
leader=`docker exec etcdclient /TopStor/etcdgetlocal.py leader`
leaderip=`docker exec etcdclient /TopStor/etcdgetlocal.py leaderip`
myhost=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternode`
myhostip=`docker exec etcdclient /TopStor/etcdgetlocal.py clusternodeip`
echo $leader | grep $myhost
if [ $? -eq 0 ];
then
	etcdip=$leaderip
else
	etcdip=$myhostip
fi
cjobs=(`echo iscsiwatchdog zfsping topstorrecvreply receivereplylooper checksyncs syncrequestlooper`)
declare  -A cmdcjobs
cmdcjobs['iscsiwatchdog']="/TopStor/iscsiwatchdoglooper.sh" 
cmdcjobs['zfsping']="/pace/zfsping.py"
cmdcjobs['topstorrecvreply']="echo"
cmdcjobs['receivereplylooper']="/TopStor/receivereplylooper.sh"
cmdcjobs['syncrequestlooper']="/pace/syncrequestlooper.sh"
cmdcjobs['checksyncs']="echo"

while true;
do
 flag=0
 /TopStor/etcdget.py $etcdip refreshdisown | grep yes 
 if [ $? -eq 0 ];
 then
  flag=1
  /TopStor/etcdput.py $etcdip refreshdisown 0 
 fi
 while [ $flag -ne 0 ];
 do
  flag=0
  rjobs=(`echo "${cjobs[@]}"`)
  echo rjobs=$rjobs
  for job in "${rjobs[@]}";
  do
	echo '###########################################'
 	echo $job
  	flag=` /TopStor/etcdget.py $etcdip refreshdisown`
 	fnkillall $job
 	isproc=`ps -ef | grep $job | grep -v color | grep -v grep | awk '{print $2}' | wc -l`
	if [ $isproc -eq 0 ];
	then
		cjobs=(`echo "${cjobs[@]}" | grep -v $job`)
		#cmd=`echo -e $cmdcjobs | grep $job`
		cmd=${cmdcjobs[$job]}
	 	echo $cmd $leaderip $myhost \& disown	>> /root/refreshtemp
	 	$cmd $leaderip $myhost & disown	
	fi
	flag=$((flag+isproc))
  	/TopStor/etcdput.py $etcdip refreshdisown $flag 
	echo flag=$flag
  done
  flag=`/TopStor/etcdget.py $etcdip refreshdisown`
  echo flaginwhile=$flag
 done
 sleep 2
done
