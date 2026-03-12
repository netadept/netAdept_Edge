''
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_file_transfer
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F
import time
import argparse
from pathlib import Path
import datetime
from netmiko import ConnectHandler, file_transfer

from jnpr.junos import Device
from jnpr.junos.utils.scp import SCP

shortdate = datetime.datetime.today().strftime("%d-%m-%Y")
home = Path.home()
nr = InitNornir(config_file=f"{home}/netadept/config.yaml") 
parser = argparse.ArgumentParser()

nr = InitNornir(config_file=f"{home}/netadept/config.yaml") 

parser.add_argument('ip_address', help='ip address of host to connect to single device')
parser.add_argument('group_one', help='group filter one to connect to multiple devices')
parser.add_argument('group_two', help='group filter two to connect to multiple devices')
parser.add_argument('filename', help='command or task that will be sent to each device')

args = parser.parse_args()
ip = (args.ip_address)
group_one = (args.group_one)
group_two = (args.group_two)
filename = (args.filename)

src = f"{home}/netadept/flask/files/{filename}"
dst = f"{filename}"


def send_file(task):
    if task.host.platform == "ios":
        results = task.run(task=netmiko_file_transfer, source_file=src, dest_file=dst, direction='put', socket_timeout=10800)
        #results = task.run(task=netmiko_file_transfer, source_file=dst, dest_file=src, direction='get', socket_timeout=10800)
        time.sleep(5)
    elif task.host.platform == "junos":
        host=ip
        user =  nr.inventory.groups['ALL'].username
        passwd =  nr.inventory.groups['ALL'].password
        port =  nr.inventory.hosts[f"{task.host}"].port

        dev = Device(host=host, user=user, passwd=passwd, port=port)
        dev.open()
        with SCP(dev, progress=True) as scp:
            scp.put(f'{src}', f'{dst}')
        dev.close()


if group_one == 'NONE':
    print(f"IP Add == {ip}")
    device = nr.filter(hostname=f"{ip}")
    results = device.run(task=send_file)
    print_result(results)

elif ip == 'None':
    print(f"IP Add == {group_one} and {group_two}")
    device = nr.filter(F(groups__contains=group_one) & F(groups__contains=group_two))
    results = device.run(task=send_file)
    print_result(results)
