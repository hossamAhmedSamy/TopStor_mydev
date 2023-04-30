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
cjobs=(`echo TopStor pacee topstorweb`)
branch=$1
branchc=`echo $branch | wc -c`
if [ $branchc -le 3 ];
then
	echo no valid branch is supplied .... exiting
	exit
fi 
flag=1
while [ $flag -ne 0 ];
do
	rjobs=(`echo "${cjobs[@]}"`)
	echo rjobs=${rjobs[@]}
	for job in "${rjobs[@]}";
	do
		echo '###########################################'
 		echo $job
		cd /$job
		if [ $? -ne 0 ];
		then
			echo the directory $job is not found... exiting
			exit
		fi
		fnupdate $branch 
		cjobs=(`echo "${cjobs[@]}" | sed "s/$job//g" `)
  	done
	echo cjobs=$cjobs
	lencjobs=`echo $cjobs | wc -c`
	echo will I iterate  $lencjobs
	if [ $lencjobs -le 3 ];
	then
		flag=0
	fi
done
cd /TopStor
echo finished
