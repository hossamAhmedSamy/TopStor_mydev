cd /pace
iscsimapping='/pacedata/iscsimapping';
runningpools='/pacedata/pools/runningpools';
myhost=`hostname -s`
hostnam=`cat /TopStordata/hostname`
poollist='/pacedata/pools/'${myhost}'poollist';
echo runningpools > $runningpools
zpool export -a
sh iscsirefresh.sh
sh listingtargets.sh
