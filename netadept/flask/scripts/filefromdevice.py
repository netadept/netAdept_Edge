
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
#import ipdb

shortdate = datetime.datetime.today().strftime("%d-%m-%Y")
home = Path.home()
nr = InitNornir(config_file=f"{home}/netadept/config.yaml") 
parser = argparse.ArgumentParser()

parser.add_argument('ip_address', help='ip address of host to connect to single device')
args = parser.parse_args()
ip = (args.ip_address)

dirlist = []

file_dir = f"{home}/netadept/flask" #  folder variable
pathlib.Path(file_dir).mkdir(exist_ok=True) # Create  folder if not already created
with open(f"{file_dir}" + "/dirfile.txt", "w") as f: # open and clear the file
    f.close()

def config(task): 
    if task.host.platform == "huawei_vrp":
        cmd = "dir"
    elif task.host.platform == "junos":
        cmd = "file list"
    elif task.host.platform == "ios":
        cmd = "dir"
    elif task.host.platform == "fortinet":
        cmd = "diag hard deviceinfo disk"

    if task.host.platform == "ios" or task.host.platform == "huawei_vrp":
        dir_result = task.run(task=send_command, command=cmd)
        task.host["dir"] = dir_result.scrapli_response.genie_parse_output()
        loc = task.host['dir']['dir']['dir']
        #ipdb.set_trace()
        for fls in task.host['dir']['dir'][f'{loc}']['files']:
            dirlist.append(fls)

    elif task.host.platform == "junos":
        dir_result = task.run(task=send_command, command=cmd)
        task.host["dir"] = dir_result.scrapli_response.genie_parse_output()
        for loc in task.host['dir']['dir']:
            file_loc = loc
        for fls, v in task.host['dir']['dir'][f'{file_loc}']['files'].items():
            dirlist.append(fls)

def wrlist():
    for fle in dirlist:
        with open(f"{file_dir}" + "/dirfile.txt", "a") as f: # open and clear the file
            f.write(fle + "\n")
            f.close()

device = nr.filter(hostname=f"{ip}")
results = device.run(task=config)
wrlist()
#print_result(results)

