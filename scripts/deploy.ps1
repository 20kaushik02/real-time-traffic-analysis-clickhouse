param (
	[switch] $MasterNode,
	[switch] $downStack,
	[string] $SwarmToken,
	[string] $ManagerAddr
)

$scriptDir = $PSScriptRoot
# Write-Output $scriptDir # ===> \Project\scripts

$stackName = "TheWebFarm"

if ($downStack)	{
	Write-Output "[+] Removing stack..."
	docker stack rm $stackName
	docker service rm registry
}
elseif ($MasterNode) {
	Write-Output "[+] swarm master"

	# cleanup
	docker stack rm $stackName
	docker service rm registry

	# data streaming
	Set-Location $scriptDir/../preprocessing
	docker service create --name registry -p 5000:5000 registry:2
	docker build -t 127.0.0.1:5000/data-streamer:latest --no-cache --push -f Dockerfile.python .

	# execute
	Set-Location $scriptDir
	docker stack deploy -d `
		-c ../preprocessing/docker-compose.yml `
		-c ../clickhouse/docker-compose-old.yaml `
		$stackName

	# scripts
	# pip install -r "$scriptDir/../final/config_update_scripts/requirements.txt"
	# Set-Location $scriptDir/../preprocessing
	# python3 update_trigger.py
}
else {
	Write-Output "[+] swarm follower"
	Write-Output "[+] joining swarm with token $SwarmToken" 
	docker swarm join --token $SwarmToken $ManagerAddr
}
