# End-to-end stack management

## Windows (Powershell)

`deploy.ps1 -MasterNode` to deploy stack with current node as manager

`deploy.ps1 -downStack` to bring down stack (run from manager node)

## Linux/macOS (Bash)

`deploy.sh -M` and `deploy.sh -D` for the same

Add `-S` if Docker requires `sudo` privileges
