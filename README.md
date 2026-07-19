netAdeptEdge

1. Centralised device access
2. Device inventory
3. Advanced group based filtering
4. Connect to device CLI in the browser
5. Retrieve information from multiple devices
6. Cisco, Juniper junos and Huawei supported (to be expanded based on demand)
7. Automate and schedule device backups
8. Transfer files from/to network devices
9. Intergrated with Zabbix monitoring suite
10. DrawIO used for network diagrams



### netAdept Setup Process ###

1. Update the system and install prerequisites
2. Install Docker and dd Docker’s official GPG key and repository (or run docker_setup.sh)
3. Clone the netAdept Repository
4. install python venv (if required)
5. install pip (if required)
6. Setup script
7. Run netAdept
8. Log in 


Once you have built an Ubuntu Server. (tested on 24.04 LTS minimum 2GB RAM and 50GB Hard drive)

1. Update the system and install prerequisites

sudo apt update && sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common   



2. Install Docker and dd Docker’s official GPG key and repository

### Add Docker’s official GPG key and repository ###

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null   

### Install Docker ###

sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin   

### remove sudo requirement for docker commands ###

sudo usermod -aG docker $USER   

reboot or log out and back in # User will no longer require sudo for docker commands 



docker --version # Verify docker installation 



3. Clone the netAdept Repository

git clone https://github.com/netadept/netAdept_Edge.git
username: netadept


### Move netadept files into home folder ###

cp -r netAdept_Edge/. .

rm -rf netAdept_Edge



4. install python venv

sudo apt install python3 python3-venv


5. install pip

sudo apt install python3-pip


6. Setup script

./setup.sh



7. Run netAdept

./netadept.sh




8. Log in 

http://ipaddress:15000/ # example: http://192.168.19.134:15000/

select : register - this will activate the default user

Proceed to login screen

default login:
username: default
password: removethisdefault
