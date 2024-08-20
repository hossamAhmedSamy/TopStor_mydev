import subprocess
import re  
from datetime import datetime, timedelta
import time

def get_zpool_status():
    # Run the zpool status command and capture the output
    result = subprocess.run(['zpool', 'status'], stdout=subprocess.PIPE, text=True) 
    pools = []
    current_pool = None
    
    for line in result.stdout.splitlines():

        if line.startswith('  pool: '):
            if current_pool:
                pools.append(current_pool)
            current_pool = {'name': line.split(': ')[1], 'details': []}
        elif current_pool is not None:
            current_pool['details'].append(line)
    
    if current_pool:
        pools.append(current_pool)
    
    return pools

def estimate_time():
    pools = get_zpool_status()
    
    
    for pool in pools:
        start_time = None
        percentage = None
        # Check if any line in 'details' contains 'DEGRADED'
        if any('DEGRADED' in detail for detail in pool['details']):
            for detail in pool['details']:
                if detail.strip().startswith('scan:'):
                    try:
                        # Attempt to find the percentage
                        match_percentage = re.search(r'(\d+\.\d+)% done', detail)
                        if match_percentage:
                            percentage = match_percentage.group(1)
                        else:
                            raise ValueError("Percentage not found in detail.")

                    except ValueError as ve:
                        print(f"Error finding percentage: {ve}")
                        continue  # Skip to next detail line

                    try:
                        # Attempt to find the start time
                        match_start_time = re.search(r'resilver in progress since ([\w\s:]+ \d{4})', detail)
                        if match_start_time:
                            start_time = match_start_time.group(1)
                        else:
                            raise ValueError("Start time not found in detail.")

                    except ValueError as ve:
                        print(f"Error finding start time: {ve}")
                        continue  # Skip to next detail line

            try:
                if start_time and percentage:
                    remaining_time = calculate_time(start_time, percentage)
                    if remaining_time is not None:
                        putTime_etcd(pool['name'], str(remaining_time))
                    else:
                        print(f"Cannot calculate remaining time for pool: {pool['name']}")
                else:
                    # Raise an error if either variable is missing
                    if not start_time:
                        raise ValueError("Missing start time.")
                    if not percentage:
                        raise ValueError("Missing percentage.")
            except ValueError as ve:
                print(f"ValueError for pool {pool['name']}: {ve}")
            except Exception as e:
                print(f"An unexpected error occurred for pool {pool['name']}: {e}")
    
    return None  # No DEGRADED pool found

def parse_time(time_str):
    """Parse a time string into a datetime object."""
    return datetime.strptime(time_str, '%a %b %d %H:%M:%S %Y')

def calculate_time(start_time_str, percentage_done):
    """Estimate the remaining time based on start time and percentage done."""
    # Convert start time to datetime object
    start_time = parse_time(start_time_str)
    
    current_time = datetime.now()
    
    elapsed_time = current_time - start_time
    # handling division by zero 
    percentage_done = float(percentage_done)
    if percentage_done == 0:
        return None  
    
    elapsed_time_minutes = elapsed_time.total_seconds() / 60
    estimated_total_time_minutes = (elapsed_time_minutes * 100) / percentage_done
    
    remaining_time_minutes = estimated_total_time_minutes - elapsed_time_minutes
    remaining_time = timedelta(minutes=remaining_time_minutes)

    print(remaining_time)
    
    return remaining_time

def putTime_etcd(pool_name, time_estimated):
    cluster_ip = "10.11.11.100"  # Replace with your actual cluster IP
    key = f"rebuilding/{pool_name}"
    value = time_estimated
    
    subprocess.run(['/TopStor/etcdput.py', cluster_ip, key, value])

if __name__ == "__main__":
    while True:
        print("hell world")
        estimate_time()
        time.sleep(120)  

