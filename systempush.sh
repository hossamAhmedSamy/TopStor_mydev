#!/usr/bin/sh
fnupdate () {
	git checkout -b $1
	#git reset --hard
	git add --all
	git commit -am 'fixing' 
	git push origin $1
	if [ $? -ne 0 ];
	then
		echo something went wrong while updating $1 .... consult the devleloper
		exit
	fi
}
cjobs=(`echo TopStor pace topstorweb`)
branch=$1
branchc=`echo $branch | wc -c`
if [ $branchc -le 3 ];
then
	echo no valid branch is supplied .... exiting
	exit
fi 
declare  -A cmdcjobs
cmdcjobs['TopStor']="TopStor" 
cmdcjobs['pace']="pace" 
cmdcjobs['topstorweb']="topstorweb" 
flag=1
while [ $flag -ne 0 ];
do
	rjobs=(`echo "${cjobs[@]}"`)
	echo rjobs=${rjobs[@]}
	for job in "${rjobs[@]}";
	do
		echo '###########################################'
 		echo $job
		fnupdate $branch 
		echo cjobsssssssssssss=${cjobs[@]}
		cjobs=(`echo "${cjobs[@]}" | sed "s/$job//g" `)
		lencjobs=`echo ${cjobs[@]} | wc -c`
		echo will I iterate  $lencjobs
  	done
	echo cjobs=$cjobs
	lencjobs=`echo $cjobs | wc -c`
	echo will I iterate  $lencjobs
	if [ $lencjobs -le 3 ];
	then
		flag=0
	fi
done
echo finished
exit
  	flag=`docker exec etcdclient /TopStor/etcdgetlocal.py refreshdisown`
        echo flaginfor $flag
 	fnkillall $job
 	isproc=`ps -ef | grep $job | grep -v color | grep -v grep | awk '{print $2}' | wc -l`
	if [ $isproc -eq 0 ];
	then
		cjobs=(`echo "${cjobs[@]}" | grep -v $job`)
		#cmd=`echo -e $cmdcjobs | grep $job`
		cmd=${cmdcjobs[$job]}
	 	echo $cmd $leaderip $myhost \& disown	>> /root/refreshtemp
	 	$cmd $leaderip $myhost >/dev/null & disown	
	fi
	flag=$((flag+isproc))
	echo flagwithiscproc=$flag
  	docker exec etcdclient /TopStor/etcdput.py etcd refreshdisown $flag 
	echo flag=$flag
  flag=`docker exec etcdclient /TopStor/etcdgetlocal.py refreshdisown`
  echo flaginwhile=$flag
 echo 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSstop'
 sleep 2
