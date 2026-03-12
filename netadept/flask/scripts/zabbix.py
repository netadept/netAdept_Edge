from nornir import InitNornir
from pathlib import Path
from zabbix_utils import ZabbixAPI

home = Path.home()
nr = InitNornir(config_file=f"{home}/netadept/config.yaml") 

api = ZabbixAPI(url="http://localhost") # Assign url to API
api.login(user='Admin', password='zabbix')   # set login credentials

hostnames = []
#zabbix_hosts = []
zabbix_allhosts = []

all_zbxhosts = api.host.get()
for zbx in all_zbxhosts:
    zbxall = zbx["host"]
    if zbxall != 'Zabbix server':
        zabbix_allhosts.append(zbxall)

###  add inventory hosts that are not 'NONE' to hostnames list if they are not in Zabbix ###
for dvc, v in nr.inventory.hosts.items():
    if dvc != 'NONE':
        hostnames.append(dvc) # add nornir hosts to hostnames list 

        ### Check whether host is already in Zabbix  ###
        #hosts = api.host.get({"filter": {"host": f"{dvc}"}}) # collect zbix hosts based on inventory hosts
        #for zab_hosts in hosts:
        #    zbix_hosts = zab_hosts["host"] 
        #    zabbix_hosts.append(zbix_hosts) # add zabbix hosts to zabbix_hosts list

#print(hostnames)
#print(zabbix_hosts)
#print(zabbix_allhosts)

for dv in hostnames:
    if dv not in zabbix_allhosts:
        print(f"this device is not on Zabbix yet: {dv}")
        ipadd = nr.inventory.hosts[f"{dv}"].hostname
        dvctype = nr.inventory.hosts[f"{dv}"].platform

        data = nr.inventory.hosts[f"{dv}"].data
        snmpver = data["ver"]
        snmpcom = data["comm"]
        snmpgrp = data["grp"]

        print(ipadd)
        print(dvctype)
        print(data)
        print(snmpver)
        print(snmpcom)
        print(snmpgrp)  

        ### Assign  correct template ID ###
        if dvctype == "huawei_vrp":
            templateid = 10229
        elif dvctype == "junos":
            templateid = 10231
        elif dvctype == "ios":
            templateid = 10218
        elif dvctype == "fortinet":
            templateid = 10604

        print(templateid)


        ### Create a group ### If group does not already exist
        try:
            api.hostgroup.create({"name": f"{snmpgrp}"})
        except Exception as e: # generic exception
            print(f"Host group {snmpgrp} already exists")
        else:
            print("something else went wrong")

        ### Parse Group ID ###
        hostgroups = api.hostgroup.get({"output": "extend", "sortfield": "name", "filter": {"name": f"{snmpgrp}"}}) # for groupid
        for grpinfo in hostgroups:
            grpid = (grpinfo["groupid"])
            print(f"group ID is: {grpid}")


        ### Create host ###
        try:
            api.host.create(
                host=f"{dv}",
                interfaces=[{
                    'type': f'{snmpver}',
                    'main': 1,
                    'useip': 1,
                    'ip': f'{ipadd}',
                    'dns': '',
                    'port': '161',
                        'details' : {
                            'version' : f'{snmpver}',
                            'community' : f'{snmpcom}',
                            'bulk' : 0,
                        }
                }],
                groups= [
                    {
                        "groupid": f"{grpid}"
                    }
                ],
                templates = [
                    {
                        "templateid": f"{templateid}"
                    }
                ],
            )
        except Exception as e:
            print("Exception name:", type(e).__name__)
            print(f"Host with the same name {dvc} already exists.")


for zb in zabbix_allhosts:
    if zb not in hostnames:
        print(f"this device needs deleting from Zabbix : {zb}")


api.logout()

