#!/bin/sh
partner=`echo $@ | awk '{print $1}'`
port=`echo $@ | awk '{print $2}'`
sleep 2
result=`nmap --max-rtt-timeout 20ms -p ${port} $partner`
echo $result | grep open 
if [ $? -eq 0 ];
then
 echo I ma here
 known=`cat /root/.ssh/known_hosts | grep -v $partner`
 echo -e "$known" > /root/.ssh/known_hosts
 scp -i /TopStordata/${partner}_keys/${partner} -P $port -o StrictHostKeyChecking=no /etc/ssh/sshd_config ${partner}:
fi
echo $result
