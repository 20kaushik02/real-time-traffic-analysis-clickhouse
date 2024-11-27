param (
	[switch] $MasterNode,
	[string] $SwarmToken,
	[string] $ManagerAddr
)

$script_dir = $PSScriptRoot
# Write-Output $script_dir # ===> \Project\scripts

if ($MasterNode) {
	Write-Output "Initializing Docker Swarm..."
	
	docker stack rm test_datastreamer_automated
	docker service rm registry
	
	# registry
	Set-Location $script_dir/../preprocessing
	
	docker service create --name registry -p 5000:5000 registry:2
	docker build -t 127.0.0.1:5000/data_streamer:latest --no-cache --push -f Dockerfile.python .
	
	docker stack deploy -d -c docker-compose.yml test_datastreamer_automated
	
	Set-Location $script_dir
	
	# data streaming
	
	# pip install -r "$script_dir/../final/config_update_scripts/requirements.txt"
}
else {
	Write-Output "swarm follower"
	Write-Output "joining swarm with token $SwarmToken" 
	docker swarm join --token $SwarmToken $ManagerAddr
}
