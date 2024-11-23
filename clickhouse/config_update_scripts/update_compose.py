import yaml
from jinja2 import Environment, FileSystemLoader
import subprocess
import json
import xml.etree.ElementTree as ET
import os

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
    
    # new shard template that is gonna be added to remote servers file of each node
    new_shard_str = f'''
        <shard>
                <weight>{curr_num_shards+1}</weight>
                <internal_replication>true</internal_replication>
                <replica>
                    <host>clickhouse-server{curr_num_servers+1}</host>
                    <port>9000</port>
                </replica>
                <replica>
                    <host>clickhouse-server{curr_num_servers+2}</host>
                    <port>9000</port>
                </replica>
            </shard>
    '''
    # extracting existing remote-servers file
    with open('../node1-config/remote-servers.xml','r') as f:
        curr_remote_servers_xml = ET.parse(f)
    
    cluster_root = curr_remote_servers_xml.find('.//cluster_1S_2R')
    new_shard_xml = ET.fromstring(new_shard_str)
    cluster_root.append(new_shard_xml)

    # creating folders for new servers that contain the configuration files
    os.makedirs(f'../node{curr_num_servers+1}-config',exist_ok=True)
    os.makedirs(f'../node{curr_num_servers+2}-config',exist_ok=True)

    # adding the new shard to each remote-servers file
    for i in range(1,curr_num_servers+3):
        output_path = f'../node{i}-config/remote-servers.xml' 
        curr_remote_servers_xml.write(output_path, encoding='utf-8', xml_declaration=False)

    env = Environment(loader=FileSystemLoader('.'))
    service_template = env.get_template('service.yml.jinja')

    # loading existing docker-compose file
    with open('../docker-compose.yaml','r') as f:
        compose_f = yaml.safe_load(f)
    
    # rendering the new service
    new_service1 = service_template.render(server_num=curr_num_servers+1)
    new_service2 = service_template.render(server_num=curr_num_servers+2)
    
    # adding the new service to docker-compose
    compose_f['services'].update(new_service1)
    compose_f['services'].update(new_service2)

    if compose_f:
        with open('../docker-compose.yaml','w') as yamlfile:
            yaml.safe_dump(compose_f, yamlfile)

    config_template = env.get_template('config.xml.jinja')
    macros_template = env.get_template('macros.xml.jinja')
    use_keeper_template = env.get_template('use-keeper.xml.jinja')

    for i in range(1,3):
        config_content = config_template.render(node_num=curr_num_servers+i)
        with open(f'../node{curr_num_servers + i}-config/config.xml','w') as f1:
            f1.write(config_content)
        
        macros_content = macros_template.render(shard_num="0{curr_num_shards}",replica_num=i)
        with open(f'../node{curr_num_servers + i}-config/macros.xml','w') as f2:
            f2.write(macros_content)
        
        use_keeper_content = use_keeper_template.render()
        with open(f'../node{curr_num_servers + i}-config/use-keeper.xml','w') as f3:
            f3.write(use_keeper_content)

