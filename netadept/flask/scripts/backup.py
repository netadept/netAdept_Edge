from nornir import InitNornir
from nornir_scrapli.tasks import send_commands
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
import pathlib
from pathlib import Path
import datetime
from pymongo import MongoClient
import uuid

shortdate = datetime.datetime.today().strftime("%d-%m-%Y")
home = Path.home()
nr = InitNornir(config_file=f"{home}/netadept/config.yaml") 

def config(task): 
    group_dir = f"{home}/netadept/flask/backups/{task.host}" # Group folder variable
    pathlib.Path(group_dir).mkdir(exist_ok=True) # Create GROUPS folder if not already created
    backupfile = f"{group_dir}" + "/" + f"backup_{task.host}_{shortdate}.txt"

    if task.host.platform == "huawei_vrp":
        cmd = ["display current", "display ip int bri", "display ip routing", "display logbuf"]
    elif task.host.platform == "junos":
        cmd = ["show config", "show interfaces terse", "show route", "show log messages"]
    elif task.host.platform == "ios":
        cmd = ["show run", "show ip int bri", "show ip route", "show log"]
    else:
        cmd = ["show run", "show ip int bri", "show ip route", "show log"]

    r = task.run(task=send_commands, commands=cmd)
    with open(f"{group_dir}" + "/" + f"backup_{task.host}_{shortdate}.txt", "a") as f:
        f.write("\n\n" + "=" * 80 + "\n" + f"DEVICE: {task.host}" + "\n" + "=" * 80 + "\n\n" )
        f.close()

    task.run(task=write_file, content=r.result, filename=str(backupfile)) #, append=True)

device = nr.filter(F(groups__contains="ALL"))
results = device.run(task=config)
print_result(results)