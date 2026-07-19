from nornir import InitNornir
from nornir_scrapli.tasks import send_command, send_commands
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
import argparse
import re
from nornir.core.filter import F
#from nornir_napalm.plugins.tasks import napalm_get
import pathlib
from pathlib import Path
import datetime
from nornir_utils.plugins.tasks.files import write_file

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

def shwint(task): # function pull interface names from "show interfaces"
    output_dir = f"{home}/netadept/flask/output" # Group folder variable
    pathlib.Path(output_dir).mkdir(exist_ok=True) # Create GROUPS folder if not already created
    with open(f"{output_dir}" + "/output.txt", "w") as f: # open and clear the groups output file
        f.close()


    if task.host.platform == "huawei_vrp":
        cmd = "dis current-config int"
    elif task.host.platform == "junos":
        cmd = 'show configuration interfaces | display set'
    elif task.host.platform == "ios":
        cmd = "show ip int brief"
    elif task.host.platform == "fortinet":
        cmd = "show system interface"
    else:
        print("Device not recognised")

    if ip != 'None':
        int_config = output_dir + "/" + "output.txt"

        with open(f"{int_config}", "w") as f: # open and clear the groups output file
            f.close()

        if task.host.platform != "ios" and task.host.platform != "fortinet":
            r = task.run(task=send_command, command=cmd)
            task.run(task=write_file, content=r.result, filename=str(int_config), append=True)

        elif task.host.platform == "fortinet":
            r = task.run(task=netmiko_send_command, command_string=cmd)
            task.run(task=write_file, content=r.result, filename=str(int_config), append=True)

        elif task.host.platform == "ios": # gets interface names and writes them to file
            r = task.run(task=send_command, command=cmd)
            task.host["int"] = r.scrapli_response.genie_parse_output()
            ints = task.host['int']['interface']
            for int, val in ints.items():
                print(int)
                try:
                    r = task.run(task=send_command, command=f"show run int {int}")
                except Exception as e:
                    pass

                task.run(task=write_file, content=r.result, filename=str(int_config), append=True)

    elif group_one != 'NONE':

        if task.host.platform != "ios" and task.host.platform != "fortinet":
            r = task.run(task=send_command, command=cmd)
            with open(f"{output_dir}" + "/output.txt", "a") as f:
                f.write("\n\n" + "=" * 80 + "\n" + f"DEVICE: {task.host}" + "\n" + "=" * 80 + "\n\n" )
                f.close()
            task.run(task=write_file, content=r.result, filename=str(output_dir) + "/" + "output.txt", append=True )

        elif task.host.platform == "fortinet":
            r = task.run(task=netmiko_send_command, command_string=cmd)
            with open(f"{config_dir}" + "/output.txt", "a") as f:
                f.write("\n\n" + "=" * 80 + "\n" + f"DEVICE: {task.host}" + "\n" + "=" * 80 + "\n\n" )
                f.close()
            task.run(task=write_file, content=r.result, filename=str(output_dir) + "/" + "output.txt", append=True )


        elif task.host.platform == "ios": # gets interface names and writes them to file
            r = task.run(task=send_command, command=cmd)
            with open(f"{output_dir}" + "/output.txt", "a") as f:
                f.write("\n\n" + "=" * 80 + "\n" + f"DEVICE: {task.host}" + "\n" + "=" * 80 + "\n\n" )
                f.close()

            task.host["int"] = r.scrapli_response.genie_parse_output()
            ints = task.host['int']['interface']
            for int, val in ints.items():
                #print(int)
                try:
                    r = task.run(task=send_command, command=f"show run int {int}")
                except Exception as e:
                    pass
                task.run(task=write_file, content=r.result, filename=str(output_dir) + "/" + "output.txt", append=True )

if group_one == 'NONE':
    print(f"IP Add == {ip}")
    device = nr.filter(hostname=f"{ip}")
    results = device.run(task=shwint)
    print_result(results)

elif ip == 'None':
    print(f"IP Add == {group_one} and {group_two}")
    device = nr.filter(F(groups__contains=group_one) & F(groups__contains=group_two))
    results = device.run(task=shwint)
    print_result(results)