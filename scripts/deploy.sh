#!/bin/bash

while getopts "SMDUT:A" flag; do
	case "${flag}" in
	S) sudoRequired=true ;;
	M) masterNode=true ;;
	D) downStack=true ;;
	U) autoShard=true ;;
	T) swarmToken=$OPTARG ;;
	A) managerAddr=$OPTARG ;;
	esac
done

scriptDir=$(dirname $(readlink -f "$0"))
# echo $scriptDir # ===> /Project/scripts

stackName="TheWebFarm"

dockerCmd="docker"
if [[ $sudoRequired ]]; then
	dockerCmd="sudo docker"
fi

if [[ $downStack ]]; then
	echo "[+] Removing stack..."
	echo "$dockerCmd stack rm $stackName"
	$dockerCmd stack rm $stackName
	$dockerCmd service rm registry
	sleep 20
	$dockerCmd volume rm $($dockerCmd volume ls --filter name=$stackName -q)
elif [[ $masterNode ]]; then
	echo "[+] swarm master"
	$dockerCmd swarm init
	
	# data streaming
	cd $scriptDir/../preprocessing
	$dockerCmd service create --name registry -p 5000:5000 registry:2
	# $dockerCmd build -t 127.0.0.1:5000/data-streamer:latest --no-cache --push -f Dockerfile.python .
	$dockerCmd build -t 127.0.0.1:5000/data-streamer:latest --push -f Dockerfile.python .

	# execute
	chmod 774 ../clickhouse/node-entrypoints/*/00_wait_for_keeper.sh
	cd $scriptDir
	$dockerCmd stack deploy -d \
		-c ../preprocessing/docker-compose.yml \
		-c ../clickhouse/docker-compose.yaml \
		-c ../ui/docker-compose.yaml \
		$stackName
else
	echo "[+] swarm follower"
	echo "[+] joining swarm with token $swarmToken"
	$dockerCmd swarm join --token $swarmToken $managerAddr
fi

if [[ $autoShard ]]; then
	cd $scriptDir
	python3 ../clickhouse/config_update_scripts/update_trigger.py
fi