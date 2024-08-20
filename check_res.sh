#!/bin/bash

ETCD_SERVER="10.11.11.249"
KEY="hosts"
PREFIX="--prefix"

# Run the etcdget.py script and capture its output
output=$(./etcdget.py $ETCD_SERVER $KEY $PREFIX)

# Check if 'DEGRADED' is in the output
if echo "$output" | grep -q "DEGRADED"; then
    echo "DEGRADED pool or raid group found."
    
    # Extract the pool or raid group name (assuming it's the key part of the key-value pair)
    degraded_pool=$(echo "$output" | grep "DEGRADED" | awk '{print $1}')
    
    # Run 'zpool status' and capture its output
    zpool_output=$(zpool status $degraded_pool)
    
    # Check if resilvering is found and extract the percentage
    if echo "$zpool_output" | grep -q "resilvering"; then
        resilvering_percentage=$(echo "$zpool_output" | grep "resilvering" | awk '{print $3}')
        echo "Resilvering found: $resilvering_percentage"
    else
        echo "No resilvering found."
    fi
else
    echo "No DEGRADED pool or raid group found."
fi

