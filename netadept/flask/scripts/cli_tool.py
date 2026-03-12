from nornir import InitNornir
from nornir_scrapli.tasks import send_command, send_commands, send_commands_from_file
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from rich import print as rprint
import argparse
from pathlib import Path
import datetime

shortdate = datetime.datetime.today().strftime("%d-%m-%Y")
home = Path.home()
nr = InitNornir(config_file=f"{home}/netadept/config.yaml") 
parser = argparse.ArgumentParser()

parser.add_argument('ip_address', help='ip address of host to connect to single device')

args = parser.parse_args()
ip = (args.ip_address)

clifile = f"{home}/netadept/flask/cli/cli_cmds.txt"
cli_outputfile = f"{home}/netadept/flask/cli/cli_out.txt"

with open(f"{cli_outputfile}", "w") as f: # open and clear the groups output file
    f.close()

def config(task): 
    r = task.run(task=send_commands_from_file, file=clifile)

    task.run(task=write_file, content=r.result, filename=str(cli_outputfile), append=True )


print(f"IP Add == {ip}")
device = nr.filter(hostname=f"{ip}")
results = device.run(task=config)
print_result(results)
