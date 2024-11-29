#!/bin/bash

set -e

keeper_hostnames=(
	"clickhouse-keeper1"
	"clickhouse-keeper2"
	"clickhouse-keeper3"
)
keeper_healthy=(false false false)

can_proceed=false

while ! $can_proceed ; do
	for keeper_idx in "${!keeper_hostnames[@]}"; do
		if wget -q --tries=1 --spider "http://${keeper_hostnames[$keeper_idx]}:9182/ready" ; then
			echo "keeper healthy"
			keeper_healthy[$keeper_idx]=true
		fi
	done
	can_proceed=true
	for keeper_idx in "${!keeper_hostnames[@]}"; do
		if ! ${keeper_healthy[$keeper_idx]} ; then
			can_proceed=false
			sleep 5
			break
		fi
	done
done
