import subprocess
import json
import re
import schedule
import time

def check_util_exec():
    # extracting details of each running container in json format    
    try:
        all_services = subprocess.check_output(["docker","stats","--no-stream","--format","json"],text=True).split('\n')[:-1]
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")

    all_services = [json.loads(s) for s in all_services]

    resource_util_exceed_flag = True            # Flag to check if all of the containers have exceeded 80% memory utilization 
    for service in all_services:
        if re.findall(r'clickhouse-server',service['Name']):
            if float(service['MemPerc'][:-1]) < 80:
                resource_util_exceed_flag = False
    
    if resource_util_exceed_flag:
        process = subprocess.Popen(['python3','update_compose.py'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()  # Wait for the process to finish and capture output
        print("Standard Output:", stdout)
        print("Standard Error:", stderr)

if __name__ == "__main__":
    schedule.every(30).seconds.do(check_util_exec)
    while True:
        schedule.run_pending()
        time.sleep(1)

        