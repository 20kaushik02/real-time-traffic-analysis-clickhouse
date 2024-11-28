#!/bin/bash

while getopts "M:D:T:A" flag; do
	case "${flag}" in
	M) masterNode=true ;;
	D) downStack=true ;;
	T) swarmToken=$OPTARG ;;
	A) managerAddr=$OPTARG ;;
	esac
done

echo "masterNode: $masterNode"
echo "downStack: $downStack"
echo "swarmToken: $swarmToken"
echo "managerAddr: $managerAddr"

$scriptDir = $(readlink -f "$0")
# echo $scriptDir # ===> /Project/scripts

$stackName="TheWebFarm"

if [[ $downStack ]]; then
	echo "[+] Removing stack..."
	docker stack rm $stackName
	docker service rm registry
elif ($MasterNode); then
	echo "[+] swarm master"

	# data streaming
	cd $scriptDir/../preprocessing
	docker service create --name registry -p 5000:5000 registry:2
	# docker build -t 127.0.0.1:5000/data-streamer:latest --no-cache --push -f Dockerfile.python .
	docker build -t 127.0.0.1:5000/data-streamer:latest --push -f Dockerfile.python .

	# execute
	cd $scriptDir
	docker stack deploy -d \
		-c ../preprocessing/docker-compose.yml \
		-c ../clickhouse/docker-compose.yaml \
		-c ../ui/docker-compose.yaml \
		$stackName

	# scripts
	# pip install -r "$scriptDir/../final/config_update_scripts/requirements.txt"
	# cd $scriptDir/../preprocessing
	# python3 update_trigger.py
else
	echo "[+] swarm follower"
	echo "[+] joining swarm with token $swarmToken"
	docker swarm join --token $swarmToken $managerAddr
fi
