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


def ping(task): 
    output_dir = f"{home}/netadept/flask/output" # Group folder variable
    pathlib.Path(output_dir).mkdir(exist_ok=True) # Create GROUPS folder if not already created
    with open(f"{output_dir}" + "/output.txt", "w") as f: # open and clear the groups output file
        f.close()

### commands to send to each device ###
        if task.host.platform == "fortinet":
            cmd = f"execute ping {}"
        else:
            cmd = f"ping {}"

    try: 
        r = task.run(task=send_commands, commands=cmd)
    except:
        print("something went wrong")

    with open(f"{output_dir}" + "/output.txt", "a") as f:
        f.write("\n\n\n\n\n" + "=" * 80 + "\n" + f"DEVICE: {task.host}" + "\n" + "=" * 80 + "\n\n" )
        f.close()
    task.run(task=write_file, content=r.result, filename=str(output_dir) + "/" + "output.txt", append=True )

if group_one == 'NONE':
    print(f"IP Add == {ip}")
    device = nr.filter(hostname=f"{ip}")
    results = device.run(task=ping)
    print_result(results)

elif ip == 'None':
    print(f"IP Add == {group_one} and {group_two}")
    device = nr.filter(F(groups__contains=group_one) & F(groups__contains=group_two))
    results = device.run(task=ping)
    print_result(results)