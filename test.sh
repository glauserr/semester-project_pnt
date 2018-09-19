#!/usr/bin/env bash

# sleep 2
wait_till_node_ready(){
	echo wait_till_node_ready
	node="$1"
	out=""
	s=0
	until [[ "$out" != "" ]]; do
		out=$(docker exec -ti "${node}" sh -c "lncli --network=simnet getinfo" | grep identity_pubkey)
		echo "${s}ms, out: (${out})"
		if [ "$s" != 0 ]; then
			sleep 0.2
		fi
		s=$(expr $s + 200)
	done
}

wait_till_synchronized(){
	echo synced
	node="$1"
	out=""
	value=""
	s=0
	until [[ "$value" = "true" ]]; do
		out=$(docker exec -ti "${node}" sh -c "lncli --network=simnet getinfo" | grep synced_to_chain)
		value=$(echo "$out" | grep -o '[a-zA-Z0-9]*' | tail -1)
		echo "${s}ms, out: ${out}"
		if [ "$s" != 0 ]; then
			sleep 0.2
		fi
		s=$(expr $s + 200)
	done	
}

btcd_ready(){	
	echo btcd_ready
	out=""
	s=0
	until [[ "$out" != "" ]]; do
		out=$(cd "$DOCKER_PATH" && o=$(docker-compose run btcctl getinfo) \
		&& echo "$o")
		echo "${s}ms, out: (${out})"
		if [ "$s" != 0 ]; then
			sleep 0.2
		fi
		s=$(expr $s + 200)
	done		
}

node=t1

create_node "$node"
# btcd_ready 
wait_till_node_ready "$node"

address=$(create_newaddress "$node")
echo "$address"

set_mining_address "$address"

echo mine blocks
mine_blocks 400

# btcd_ready
wait_till_synchronized "$node"

get_balance "$node"





