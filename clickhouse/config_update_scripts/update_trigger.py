import subprocess
import json
import re
import schedule
import time

def check_util_exec():
    print("Performing check")
    # extracting details of each running container in json format    
    try:
        all_services = subprocess.check_output(["sudo", "docker","stats","--no-stream","--format","json"],text=True).split('\n')[:-1]
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")

    all_services = [json.loads(s) for s in all_services]

    resource_util_exceed_flag = True # Flag to check if all of the containers have exceeded 80% memory utilization 
    for service in all_services:
        if re.findall(r'clickhouse-server',service['Name']):
            if float(service['MemPerc'][:-1]) < 50:
                resource_util_exceed_flag = False
    
    if resource_util_exceed_flag:
        print("Config update triggered")
        process = subprocess.Popen(['python3','../clickhouse/config_update_scripts/update_compose.py'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()  # Wait for the process to finish and capture output
        print("Standard Output:", stdout)
        print("Standard Error:", stderr)
        if stdout:
            redeploy  = subprocess.Popen(['docker','stack','deploy','-d','-c','../preprocessing/docker-compose.yml','-c','../clickhouse/docker-compose.yaml','-c','../ui/docker-compose.yaml','TheWebFarm'])
            stdout1, stderr1= redeploy.communicate()  # Wait for the process to finish and capture output
            print("Standard Output:", stdout1)
            print("Standard Error:", stderr1)
            time.sleep(120)
        # try:
        #     all_services = subprocess.check_output(["sudo", "docker","stats","--no-stream","--format","json"],text=True).split('\n')[:-1]
        # except subprocess.CalledProcessError as e:
        #     print(f"Command failed with return code {e.returncode}")

if __name__ == "__main__":
    # schedule.every(30).seconds.do(check_util_exec)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    while True:
        check_util_exec()
        time.sleep(30)
        