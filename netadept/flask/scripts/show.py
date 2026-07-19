from nornir import InitNornir
from nornir_scrapli.tasks import send_command, send_commands
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from rich import print as rprint
import pathlib
import os
import argparse
from pathlib import Path
import datetime

shortdate = datetime.datetime.today().strftime("%d-%m-%Y")
home = Path.home()
nr = InitNornir(config_file=f"{home}/netadept/config.yaml") 
parser = argparse.ArgumentParser()

parser.add_argument('ip_address', help='ip address of host to connect to single device')
parser.add_argument('group_one', help='group filter one to connect to multiple devices')
parser.add_argument('group_two', help='group filter two to connect to multiple devices')
parser.add_argument('show_command', help='command or task that will be sent to each device')

args = parser.parse_args()
ip = (args.ip_address)
group_one = (args.group_one)
group_two = (args.group_two)
show_command = (args.show_command)

print(ip)
print(group_one)
print(group_two)


def config(task): 
    output_dir = f"{home}/netadept/flask/output" # Group folder variable
    pathlib.Path(output_dir).mkdir(exist_ok=True) # Create GROUPS folder if not already created
    with open(f"{output_dir}" + "/output.txt", "w") as f: # open and clear the groups output file
        f.close()

### commands to send to each device ###
    if show_command == 'configuration':
        if task.host.platform == "huawei_vrp":
            cmd = ["display current"]
        elif task.host.platform == "junos":
            cmd = ["show config | display set"]
        elif task.host.platform == "ios":
            cmd = ["show run"]
        elif task.host.platform == "fortinet":
            cmd = "show"

    elif show_command == 'check_Config_saved':
        if task.host.platform == "huawei_vrp":
            cmd = ["compare configuration"]
        elif task.host.platform == "junos":
            cmd = ["show configuration | compare"]
        elif task.host.platform == "ios":
            cmd = ["sho archive config differences"]
        elif task.host.platform == "fortinet":
            cmd = "show | grep admin-sport -f"

    elif show_command == 'ip_interfaces':
        if task.host.platform == "huawei_vrp":
            cmd = ["display ip int bri"]
        elif task.host.platform == "junos":
            cmd = ["show interfaces terse"]
        elif task.host.platform == "ios":
            cmd = ["show ip int bri"]
        elif task.host.platform == "fortinet":
            cmd = "get system interface physical"
        
    elif show_command == 'interfaces':
        if task.host.platform == "huawei_vrp":
            cmd = ["display interfaces"]
        elif task.host.platform == "junos":
            cmd = ["show interfaces "]
        elif task.host.platform == "ios":
            cmd = ["show interfaces"]
        elif task.host.platform == "fortinet":
            cmd = "get system interface physical"
            
    elif show_command == 'vrrp':
        if task.host.platform == "huawei_vrp":
            cmd = ["display vrrp"]
        elif task.host.platform == "junos":
            cmd = ["show vrrp"]
        elif task.host.platform == "ios":
            cmd = ["show vrrp", "show standby"]
        elif task.host.platform == "fortinet":
            cmd = "get system ha status"
            
    elif show_command == 'routing_table':
        if task.host.platform == "huawei_vrp":
            cmd = ["display ip routing"]
        elif task.host.platform == "junos":
            cmd = ["show route"]
        elif task.host.platform == "ios":
            cmd = ["show ip route"]
        elif task.host.platform == "fortinet":
            cmd = "get router info routing-table all"
            
    elif show_command == 'version':
        if task.host.platform == "huawei_vrp":
            cmd = ["display version"]
        elif task.host.platform == "junos":
            cmd = ["show version"]
        elif task.host.platform == "ios":
            cmd = ["show version"]
        elif task.host.platform == "fortinet":
            cmd = "get system status "
            
    elif show_command == 'acl':
        if task.host.platform == "huawei_vrp":
            cmd = ["display acl all"]
        elif task.host.platform == "junos":
            cmd = ["show configuration security | disp set"]
        elif task.host.platform == "ios":
            cmd = ["show ip access"]
        elif task.host.platform == "fortinet":
            cmd = "get router access-list"
            
    elif show_command == 'syslog':
        if task.host.platform == "huawei_vrp":
            cmd = ["display logbuf"]
        elif task.host.platform == "junos":
            cmd = ["show log messages"]
        elif task.host.platform == "ios":
            cmd = ["show log"]
        elif task.host.platform == "fortinet":
            cmd = "execute log display"
            
    elif show_command == 'lldp':
        if task.host.platform == "huawei_vrp":
            cmd = ["dis lldp neighbor"]
        elif task.host.platform == "junos":
            cmd = ["show lldp neigh"]
        elif task.host.platform == "ios":
            cmd = ["show lldp neighbors detail"]
        elif task.host.platform == "fortinet":
            cmd = "get system interface physical"

    elif show_command == 'arptable':
        if task.host.platform == "huawei_vrp":
            cmd = ["display arp"]
        elif task.host.platform == "junos":
            cmd = ["show arp", "show ethernet-switching table brief"]
        elif task.host.platform == "ios":
            cmd = ["show arp", "show mac-add"]
        elif task.host.platform == "fortinet":
            cmd = "get sys arp"
            
    elif show_command == 'user':
        if task.host.platform == "huawei_vrp":
            cmd = ["disp current | i user"]
        elif task.host.platform == "junos":
            cmd = ["show configuration | display set | match user"]
        elif task.host.platform == "ios":
            cmd = ["sho running-config | i username"]
        elif task.host.platform == "fortinet":
            cmd = "get system interface physical"
            
    elif show_command == 'file_system':
        if task.host.platform == "huawei_vrp":
            cmd = ["dir"]
        elif task.host.platform == "junos":
            cmd = ["file list"]
        elif task.host.platform == "ios":
            cmd = ["dir"]
        elif task.host.platform == "fortinet":
            cmd = "diag hard deviceinfo disk"

    elif show_command == 'time':
        if task.host.platform == "huawei_vrp":
            cmd = ["display clock"]
        elif task.host.platform == "junos":
            cmd = ["show system uptime"]
        elif task.host.platform == "ios":
            cmd = ["show clock"]
        elif task.host.platform == "fortinet":
            cmd = "get system status"

    elif show_command == 'environment':
        if task.host.platform == "huawei_vrp":
            cmd = ["display environment"]
        elif task.host.platform == "junos":
            cmd = ["show chassis environment"]
        elif task.host.platform == "ios":
            cmd = ["show environment"]
        elif task.host.platform == "fortinet":
            cmd = "get system status"

    elif show_command == 'snmp':
        if task.host.platform == "huawei_vrp":
            cmd = ["display snmp statistics"]
        elif task.host.platform == "junos":
            cmd = ["show snmp statistics"]
        elif task.host.platform == "ios":
            cmd = ["show snmp"]
        elif task.host.platform == "fortinet":
            cmd = " "

    elif show_command == 'history':
        if task.host.platform == "huawei_vrp":
            cmd = ["display history-command"]
        elif task.host.platform == "junos":
            cmd = ["show cli history"]
        elif task.host.platform == "ios":
            cmd = ["show history all"]
        elif task.host.platform == "fortinet":
            cmd = " "

    try: 
        if task.host.platform == "fortinet":
            r = task.run(task=netmiko_send_command, command_string=cmd)
        else:
            r = task.run(task=send_commands, commands=cmd)
    except:
        print("something")

    with open(f"{output_dir}" + "/output.txt", "a") as f:
        f.write("\n\n\n\n\n" + "=" * 80 + "\n" + f"DEVICE: {task.host}" + "\n" + "=" * 80 + "\n\n" )
        f.close()
    task.run(task=write_file, content=r.result, filename=str(output_dir) + "/" + "output.txt", append=True )

if group_one == 'NONE':
    print(f"IP Add == {ip}")
    device = nr.filter(hostname=f"{ip}")
    results = device.run(task=config)
    print_result(results)

elif ip == 'None':
    print(f"IP Add == {group_one} and {group_two}")
    device = nr.filter(F(groups__contains=group_one) & F(groups__contains=group_two))
    results = device.run(task=config)
    print_result(results)