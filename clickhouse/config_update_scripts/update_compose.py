import yaml
from jinja2 import Environment, FileSystemLoader
import subprocess
import json
if __name__ == "__main__":
    
    # extracting details of each running container in json format    
    try:
        all_services = subprocess.check_output(["docker","ps","--format","json"],text=True).split('\n')[:-1]
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")

    all_services = [json.loads(s) for s in all_services]
    # extracting the name, removing the custom id from it and storing it in a list
    all_service_names = [service['Names'].split('.')[0] for service in all_services]
    # extracting only 'keeper1', 'server1'...
    all_service_names = [ name.split('-')[-1] for name in all_service_names]

    # removing all keeepers
    all_service_names.remove('keeper1')
    all_service_names.remove('keeper2')
    all_service_names.remove('keeper3')
    curr_num_servers = sorted(all_service_names)[-1][-1]

    replication_factor = 2
    curr_num_shards = curr_num_servers/replication_factor

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('service.yml.jinja')

    with open('../docker-compose.yaml','r') as f:
        compose_f = yaml.safe_load(f)
    
    new_service1 = template.render(server_num=curr_num_servers+1)
    new_service2 = template.render(server_num=curr_num_servers+1)

    compose_f['services'].update(new_service1)
    compose_f['services'].update(new_service2)

    if compose_f:
        with open('../docker-compose.yaml','w') as yamlfile:
            yaml.safe_dump(compose_f, yamlfile)