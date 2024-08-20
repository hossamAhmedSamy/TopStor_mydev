#!/usr/bin/env python3
import subprocess
import re
import time

def get_zpool_status():
    # Execute the `zpool status` command and capture the output
    result = subprocess.run(['zpool', 'status'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def parse_resilvering_data(status_output):
    # Check if the pool state is DEGRADED
    if 'state: DEGRADED' in status_output:
        # Regular expression to find the resilvered line
        resilver_regex = re.compile(r'resilvered (\d+(\.\d+)?)M in (\d{2}):(\d{2}):(\d{2})')
        match = resilver_regex.search(status_output)

        if match:
            # Extract the amount of data resilvered
            data_resilvered = float(match.group(1))  # in megabytes
            time_taken = f"{match.group(3)}:{match.group(4)}:{match.group(5)}"  # Extracted time in HH:MM:SS format
            return data_resilvered, time_taken
    return None, None

# Main loop to continuously check the status
while True:
    zpool_status_output = get_zpool_status()
    data_resilvered, time_taken = parse_resilvering_data(zpool_status_output)

    if data_resilvered is not None:
        print(f"State: DEGRADED. Data Resilvered: {data_resilvered} MB. Time Taken: {time_taken}")
    else:
        print("State: ONLINE or No resilvering information found.")

    # Wait for 2 seconds before checking again
    time.sleep(2)

