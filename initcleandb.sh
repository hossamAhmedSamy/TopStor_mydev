#!/bin/sh
export ETCDCTL_API=3
etcdctl --user=root:YN-Password_123 --endpoints=10.11.11.244:2379 endpoint status -w table
/pace/etcstats.py compact `/pace/etcstats.py  endpoint status --write-out="json" | egrep -o '"revision":[0-9]*' | egrep -o '[0-9]*'`
/pace/etcstats.py defrag
etcdctl --user=root:YN-Password_123 --endpoints=10.11.11.244:2379 endpoint status -w table



