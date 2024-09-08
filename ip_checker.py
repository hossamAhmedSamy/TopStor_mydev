#!/usr/bin/env python3

import argparse
import re
from etcdget import etcdget  # Importing the etcdget function directly



def getClusterIp():
    try:
        # Use etcdget to retrieve the cluster node IP
        result = etcdget('10.11.11.100', 'clusternodeip', '--prefix')
        
        # Extract IP addresses using regex
        pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        for entry in result:
            match = re.search(pattern, entry[1])
            if match:
                clusterIp = match.group()
                return clusterIp
        raise ValueError("No IP address found in output")
        
    except Exception as e:
        raise ValueError(f"An error occurred while retrieving the cluster IP: {e}")

def check_ip_uniqueness(ip, vtype ):
    try:
        # Fetch volume data using etcdget
        result = etcdget('10.11.11.100', 'volumes', '--prefix')
        
        # Exact match regex for IP address
        ip_pattern = rf'\b{re.escape(ip)}\b'  # Escape the IP address and match as a whole word

        # Iterate through the results and check for exact IP and vtype match
        for line in result:
            volume_key, volume_value = line
            if re.search(ip_pattern, volume_value):  # Check for exact IP match
                if vtype.upper() in volume_key:
                    print("Invalid IP")
                    return 1
        
        print("Valid IP")
        return 0

    except Exception as e:
        print(f"An error occurred while checking IP uniqueness: {e}")
        return 1




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if an IP is valid and does not conflict with existing IPs.")
    parser.add_argument("ip", type=str, help="The IP address to check.")
    parser.add_argument("vtype", type=str.upper, choices=['CIFS', 'HOME', 'NFS', 'ISCSI'], help="The type of the IP address (CIFS, HOME, NFS, ISCSI).")

    args = parser.parse_args()

    ip_to_check = args.ip
    vtype = args.vtype

    exit_code = check_ip_uniqueness(ip_to_check, vtype)
    exit(exit_code)
