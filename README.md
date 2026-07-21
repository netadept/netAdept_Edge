
# netAdeptEdge

#### Centralised device access
#### Device inventory
#### Advanced group based filtering
#### Connect to device CLI in the browser
#### Retrieve information from multiple devices
#### Cisco, Juniper junos and Huawei supported (to be expanded based on demand)
#### Automate and schedule device backups
#### Transfer files from/to network devices
#### Intergrated with Zabbix monitoring suite
#### DrawIO used for network diagrams



# netAdept Setup Process

#### 1. Update the system and install prerequisites
#### 2. Install Docker and dd Docker’s official GPG key and repository (or run docker_setup.sh)
#### 3. Clone the netAdept Repository
#### 4. install python venv (if required)
#### 5. install pip (if required)
#### 6. Setup script
#### 7. Run netAdept
#### 8. Log in




+ Tested on 24.04 LTS 
+ Minimum 2GB RAM and 50GB Hard drive


# 1. Update the system and install prerequisites

	sudo apt update && sudo apt upgrade -y
	sudo apt install -y apt-transport-https ca-certificates curl software-properties-common


# 2. Install Docker and dd Docker’s official GPG key and repository

## Add Docker’s official GPG key and repository 

	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
	echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null


## Install Docker 

	sudo apt-get update
	sudo apt-get install docker-ce docker-ce-cli containerd.io


## remove sudo requirement for docker commands 

	sudo usermod -aG docker $USER
	
## Reload "docker" group for changes to take effect

	newgrp docker

+ If "newgrp docker" does not work reboot or log out and back in


## Verify docker installation

	docker --version
	docker ps


## Clone the netAdept Repository

	git clone https://github.com/netadept/netAdept_Edge.git


## Move netadept files into home folder #

	cp -r netAdept_Edge/. .
	rm -rf netAdept_Edge


## 4. install python venv

	sudo apt install python3 python3-venv


## 5. install pip

	sudo apt install python3-pip


## 6. Setup script

	./setup.sh


## 7. Run netAdept

	./netadept.sh


## 8. Log in

	http://ipaddress:15000/ 

+ select : register - this will activate the default user

## Proceed to login screen

### default username:

	default

### default password:

	removethisdefault









