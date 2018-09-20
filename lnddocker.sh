#!/usr/bin/env bash

########
# INIT #
########
export DOCKER_PATH="${GOPATH}/src/github.com/lightningnetwork/lnd/docker"

# make sure btcd use simnet. 
export NETWORK="simnet"

# log file
# echo new execution, start log >> log.txt


#######################
# Functions (helpers) #
#######################
# input: <object> <key>
# Note: does not work for multiple appearance of the key
get_value() {
	obj="$1"
	key="$2"
	# echo "${obj}" | grep -o "\"${key}\": \"[0-9a-zA-Z[:space:]]*\"" \
	# | sed -e "s/${key}//" | grep -o ': "[0-9a-zA-Z[:space:]]*"'	

	echo "${obj}" | grep -o "\"${key}\": \"[0-9a-zA-Z[:space:]]*\"" \
	| sed -e "s/${key}//" | grep -o '"[0-9a-zA-Z[:space:]]*"' \
	| tail -1 | grep -o '[0-9a-zA-Z[:space:]]*'
}

log(){
	msg="$1"
	echo "$msg" >> log.txt
}

# input: <container>
container_exists(){
	con="$1"	
	exit=false
	if [[ -n $(docker ps -a | grep "${con}") ]]; then
		exit=true
	fi
	log "container_exists: ${con}? ${exit}"
	echo "$exit"
}

# input: <container>
wait_for_existance(){
	con="$1"
	timeout=-1
	if [ "$#" -gt 1 ] && [ "$2" -gt -1 ]; then
		timeout=$(expr "$2" - 1)
	fi

	polling=200
	timer=0

	while [[ $(container_exists "$con") != true ]]; do
		sleep $(printf %.3f\\n "$((${polling}))e-3")
		timer=$(expr "$timer" + "$polling")
		log "Wait $timer"
		if [ "$timeout" -gt -1 ] && [ "$timer" -gt "$timeout" ]; then
			log "Error: wait_for_existance, timeout ${timeout}ms raised!" 
			# echo Error: timeout
			break
		fi
	done
}


####################
# Functions (main) #
####################

# input: <node (e.g n0)> <bash cmd> <grep for (optional)>
# return: output of <bash cmd>
# note: starts a bash shell of the node and run cmd in it
run_node_bashCmd() {
	node="$1"
	cmd="$2"
	if [[ $# -gt 2 ]]; then
		docker exec -ti "$node" sh -c "$cmd" | grep "$3"
		# log run_node_bashCmd: node: "$node", cmd: "$cmd", grep "$3"
	else
		docker exec -ti "$node" sh -c "$cmd"
	fi
}

cleanup(){
	. cleanup.sh
}

# input: <node (e.g. n0)>
create_node(){
	node="$1"
	out=""
	out=$(cd "$DOCKER_PATH" && o=$(docker-compose run -d --name "$node" lnd_btc) \
		&& echo "$o")
	log "creating node ${node}.., created. ${out}"
	echo "$out"
}

# input: <node (e.g. n0)>
wait_till_node_ready(){
	node="$1"
	out=""
	s=0
	until [[ "$out" != "" ]]; do
		out=$(docker exec -ti "${node}" sh -c "lncli --network=simnet getinfo" | grep identity_pubkey)
		if [ "$s" != 0 ]; then
			sleep 0.2
		fi
		s=$(expr $s + 200)
	done
	log "$node ready"
}

# input: <node (e.g. n0)>
create_newaddress() {
	node="$1"  	
  	cmd='lncli --network=simnet newaddress np2wkh'
  	grep='address'

  	var=$(run_node_bashCmd "$node" "$cmd" "$grep")
  	address=$(echo $var | grep -o '[a-zA-Z0-9]*' | tail -1)
  	log "created address, node: ${node}, address:${address}"

  	echo $address
}

# input: <node address>
set_mining_address() {
	address="$1"
  	(cd "$DOCKER_PATH" && MINING_ADDRESS=$address docker-compose up -d btcd)
  	log "set_mining_address: ${address}"
  	# wait_for_existance btcd 10000
}

# input: <number of blocks>
mine_blocks() {
	nblocks="$1"  	
	out=$(cd "$DOCKER_PATH" && o=$(docker-compose run btcctl generate "$nblocks") \
		&& echo "$o")
  	log "mining ${nblocks}, out: ${out}"
}

# input: <node (e.g. n0)>
wait_till_synchronized(){
	node="$1"
	out=""
	value=""
	s=0
	until [[ "$value" = true ]]; do
		out=$(docker exec -ti "${node}" sh -c "lncli --network=simnet getinfo" | grep synced_to_chain)
		value=$(echo "$out" | grep -o '[a-zA-Z0-9]*' | tail -1)
		if [ "$s" != 0 ]; then
			sleep 0.2
		fi
		s=$(expr $s + 200)
	done	
}
	
# input: <node (e.g. n0)> 
get_balance() {
	node="$1"
	cmd='lncli --network=simnet walletbalance'
	run_node_bashCmd "$node" "$cmd"
}

# input: <node (e.g. n0)> 
get_pubKey() {
	node="$1"
	cmd='lncli --network=simnet getinfo'
	grep='identity_pubkey'
	var=$(run_node_bashCmd "$node" "$cmd" "$grep")
	value=$(echo $var | grep -o '[a-zA-Z0-9]*' | tail -1)
	echo $value
}

# input: <node (e.g. n0)> 
get_IP() {
	node="$1"
	pattern='[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}'
	docker inspect "$node" | grep IPAddress | grep -o "$pattern"
}

# input: <node>
list_channels() {
	run_node_bashCmd "$1" 'lncli --network=simnet listchannels'
}

# input: <node1>
list_channelpoints() {
	node="$1"
	list_channels "$node" | grep channel_point | sed -e 's/"channel_point"://' \
	| grep -o '[0-9a-z]*:[0-9]'	
}

# input: <node1> <node2>
connect_2nodes() {
	node1="$1"
	node2="$2"
	pubkey=$(get_pubKey "$node2")
	host=$(get_IP "$node2")
	cmd="lncli --network=simnet connect ${pubkey}@${host}"
	out=$(run_node_bashCmd "$node1" "$cmd")
	log "connecting $node1 and $node2. ${pubkey}@${host}"
	log "connect_2nodes: ${out}"
	# echo "$node1 - $node2 connected"
}

# input: <node1> <node2>
is_connected(){
	node1="$1"
	node2="$2"
	retVal=false
	pubkey1=$(get_pubKey "$node1")
	pubkey2=$(get_pubKey "$node2")
	# echo "$pubkey1, $pubkey2"
	cmd="lncli --network=simnet listpeers"
	if [ -n "$pubkey1" ] && [ -n "$pubkey2" ]; then
		out1=$(run_node_bashCmd "$node1" "$cmd" "$pubkey2")
		out2=$(run_node_bashCmd "$node2" "$cmd" "$pubkey1")

		# echo "(${out1})"
		# echo "(${out2})"
		if [ -n "$out1" ] && [ -n "$out2" ]; then
			retVal=true
		fi
	fi
	echo "$retVal"
}

# input: <node1> <node2>
wait_till_connected(){
	node1="$1"
	node2="$2"
	until [[ $(is_connected "$node1" "$node2") = true ]]; do
		sleep 0.2
	done
	log "$node1 - $node2 connected"
}


# input: <node1> <node2> <capital>
# note: there is a max channel size of 0.16777215 BTC
open_channel(){
	node1="$1"
	node2="$2"
	captial="$3"	
	pubkey=$(get_pubKey $node2)
	cmd="lncli --network=simnet openchannel --node_key=$pubkey --local_amt=$captial"
	obj=$(run_node_bashCmd "$node1" "$cmd")
	funding_txid=$(get_value "$obj" 'funding_txid')
	if [[ -n $funding_txid ]]; then
		echo "$funding_txid"
		log "${node1} '<->' ${node2} channel created, funding_txid:${funding_txid}" 
	else
		echo 0
		log "Error! ${node1} '<->' ${node2} channel NOT created: ${obj}"
	fi
}

# input: <node> <funding_txid>
is_open(){
	node="$1"
	funding_txid="$2"
	retVal=false
	exists=$(list_channels "$node" | grep -o "$funding_txid")
	log "is_open: exists: $exists"
	if [[ -n "$exists" ]]; then
		retVal=true
	fi
	echo "$retVal"
}

wait_till_opened(){
	node="$1"
	txid="$2"
	until [[ $(is_open "$node" "$txid") = true ]]; do
		sleep 0.2
	done
	log "$node: $txid, channel is open"	
}

# input: <node1> <funding_txid>
close_channel(){
	node="$1"
	funding_txid="$2"
	cmd="lncli --network=simnet closechannel ${funding_txid}"
	run_node_bashCmd "$node" "$cmd"
}

# input: <node1> <node2> <amount>
# note: <node1> pays <node2>
send_payment() {
	node1="$1"
	node2="$2"
	amount="$3"

	retVal=failed
	# add invoice on node2 side
	cmd="lncli --network=simnet addinvoice --amt=${amount}"
	grep='pay_req\|r_hash'
	obj=$(run_node_bashCmd "$node2" "$cmd" "$grep")
	# r_hash=$(get_value obj r_hash)
	pay_req=$(get_value "$obj" 'pay_req')

	# send payment from node1 to node2 
	cmd="echo yes | lncli --network=simnet sendpayment --pay_req=${pay_req}"
	out=$(run_node_bashCmd "$node1" "$cmd")
	error=$(get_value "$out" 'payment_error')
	if [[ -z "$error" ]]; then
		log "send_payment, ${node1} to ${node2}, amount: ${amount}. Success: ${out}"
		retVal=successful
	else
		log "send_payment, ${node1} to ${node2}, amount: ${amount}. Failed: ${out}"
	fi
	echo "$retVal"
}

########
# Main #
########
# main(){	

# 	export NETWORK="simnet"

# 	echo Hello, how many nodes should be created?

# 	isOk=0
# 	N_nodes=0
# 	until [[ $isOk == 1 ]]; do
# 		read N_nodes

# 		if [[ $N_nodes =~ ^[0-9]+$ ]] #regex
# 		then
# 		    echo $N_nodes
# 		    isOk=1
# 		else
# 			echo Input a number!
# 		fi
# 	done

# 	cleanup

# 	for (( i = 0; i < $N_nodes; i++ )); do
# 	 	create_node "n$i" # n0.. n<N_nodes>
# 	 	# TODO: remove that such that next cmd start when previous finished.
# 	 	sleep 5 # wait until rpc sever created in lnd_btc is ready
# 	done

# 	address=$(create_newaddress n0)
# 	set_mining_address "$address"
# 	mine_blocks 100 # mine at least 100 (genesis blocks)
# 	sleep 5 # TODO: remove that such that next cmd start when previous finished. 
# 	(cd "$DOCKER_PATH" && docker-compose run btcctl getblockchaininfo | grep -A 1 segwit)
# 	get_balance n0
# 	# get_pubKey n0 
# 	# get_IP n0
# 	connect_2nodes n0 n1
# 	open_channel n0 n1 100000
# 	mine_blocks 3
# }


	