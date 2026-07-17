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
parser.add_argument('filename', help='File to upload from device')

args = parser.parse_args()
ip = (args.ip_address)
filename = (args.filename)

src = f"{home}/netadept/flask/files/{filename}"
dst = f"{filename}"

def send_file(task):
    if task.host.platform == "ios":
        #results = task.run(task=netmiko_file_transfer, source_file=src, dest_file=dst, direction='put', socket_timeout=10800)
        task.run(task=netmiko_file_transfer, source_file=filename, dest_file=src, direction='get', socket_timeout=10800)
        print(filename)
        time.sleep(5)
    elif task.host.platform == "junos":
        host=ip
        user =  nr.inventory.hosts[f'{task.host}'].username
        passwd =  nr.inventory.hosts[f'{task.host}'].password
        port =  nr.inventory.hosts[f"{task.host}"].port
        dev = Device(host=host, user=user, passwd=passwd, port=port)
        dev.open()
        with SCP(dev, progress=True) as scp:
            scp.get(f'{dst}', f'{src}')
        dev.close()

device = nr.filter(hostname=f"{ip}")
results = device.run(task=send_file)
print_result(results)
