# Semester Project - Exploring Centralized Payment Network Topology


Setting up lighning network on local machine:

SETUP:

	1. install docker and docker-compose
	2. checkout lightning git-repo lightningnetwork/lnd
	3. install python3 and pip3
	4. install python modules: 
		$ pip3 install shellfuncs
		$ pip3 install matplotlib
		$ pip3 install networkx

	5. packages:
	sudo apt-get install python3-tk


CONFIG:

	Set permission to docker engine:
		$ sudo usermod -a -G docker $USER


	Docker for lnd:
	https://github.com/lightningnetwork/lnd/tree/master/docker


RUN:

	python3 topology.py
