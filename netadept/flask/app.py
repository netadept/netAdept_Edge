import os
from flask import Flask, render_template, request, url_for, flash, redirect, session, jsonify, Response, send_file
from nornir import InitNornir
from nornir_scrapli.tasks import send_command, send_commands, send_commands_from_file
from nornir_netmiko.tasks import netmiko_send_command, netmiko_file_transfer, netmiko_multiline
from nornir.core.filter import F
import subprocess
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, BooleanField, DateTimeField, 
                     SelectField, RadioField, TextAreaField)
from wtforms.validators import DataRequired
from wtforms.fields import DateField, EmailField, TelField
import uuid
from pymongo import MongoClient
import datetime
from passlib.hash import pbkdf2_sha256
import functools 
import re
from jinja2 import Template
from pathlib import Path
import time
from werkzeug.utils import secure_filename
import pathlib
import string
import random
import ipaddress
import click
from crontab import CronTab
from pathlib import Path
import getpass

current_user = getpass.getuser()   


home = Path.home()
shortdate = datetime.datetime.today().strftime("%d-%m-%Y")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisaasdikfnlkmnSK123' # encrypt and decrypts session data
nr = InitNornir(config_file=f"{home}/netadept/config.yaml") 

###### some global varaiables #####
showScripts = ["devices", "device_details", "route_table", "version", "arp", "dir", "ip_interfaces", "interface_details", "cdp_neighbors", "configuration", "access_lists", "nat_translations"]
grouplist=nr.inventory.groups.values() # turns the nornir inventry groups into a variable 
hostlist = list(nr.inventory.hosts.keys()) # turns the nornir inventry hosts into a variable 

##### MongoDB ATLAS #####

#client = MongoClient("mongodb+srv://africasean:rcJxUJvGS9xv7Kxb@mongotest.rgw9hif.mongodb.net/userlogin")
#app.db = client.mongotest

##### MongoDB Local #####

client = MongoClient('localhost', 27017, username='root', password='netadept')
app.db = client.netadeptdb
hostinfo = app.db.hostgrps
authdusr = app.db.authed_users

### Login Guard ###

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("login"))
        return route(*args, **kwargs)
    return route_wrapper

### Error Page ###

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

### Working Directory ###

basedir = os.path.abspath(os.path.dirname(__file__)) # grabs absolute path for directory name using OS : /home/singlepoint/singlepoint/flask
print("#####################################################################################################################################")
print(f"The directory for Flask is: {basedir}")
print("#####################################################################################################################################")

### WTForm ###

#class InfoForm(FlaskForm):
#    email = StringField("Please enter your email: ", validators=[DataRequired()])
#    username = StringField("Please enter your username: ", validators=[DataRequired()])
#    pre_password = StringField("Please enter your password: ", validators=[DataRequired()])
#    submit = SubmitField("  Register  ")


#########################################################################################################

##### Base Template #####

@app.route("/secondbase", methods=["POST", "GET"])
@login_required
def secondbase():
    if request.method == "POST":
        singleselect = request.form["singleselect"] 
        session["singleselect"] = singleselect 
        device_ip = nr.inventory.hosts[f"{singleselect}"].hostname
        #if request.form.get("Refresh-btn"):
        #    acl_ext = subprocess.run(["python", "scripts/view_scripts/acl_ext.py", f"{device_ip}"])
        #    acl = subprocess.run(["python", "scripts/view_scripts/acl.py", f"{device_ip}"])
        #    interfaces = subprocess.run(["python", "scripts/view_scripts/interfaces.py", f"{device_ip}"])
        #    routing = subprocess.run(["python", "scripts/view_scripts/routing.py", f"{device_ip}"])
        #    version = subprocess.run(["python", "scripts/view_scripts/version.py", f"{device_ip}"])
        return render_template("secondbase.html", hostlist=hostlist)  
    else:
        return render_template("secondbase.html", hostlist=hostlist)    

### Some Testing to be deleted !!! ###

@app.route("/base/", methods=["POST", "GET"])
@login_required
def base():
    if request.method == "POST":
        return render_template("base.html")  
    else:
        return render_template("base.html")    

@app.route("/topbar/", methods=["POST", "GET"])
@login_required
def topbar():
    if request.method == "POST":
        return render_template("base_topbar.html")  
    else:
        return render_template("base_topbar.html")    
    
@app.route("/testpage/", methods=["POST", "GET"])
@login_required
def testpage():
    if request.method == "POST":
        return render_template("basetestpage.html")  
    else:
        return render_template("basetestpage.html")  
    
#########################################################################################################

# Dashboard

@app.route("/", methods=["POST", "GET"])
def dashboard():
    if request.method == "POST":
        return redirect(url_for('dashboard'))
    else:
        return render_template("dashboard.html", hostlist=hostlist)
    #return render_template('error.html'), 404

# Register

@app.route("/register/", methods=["POST", "GET"])
def register():
    # Create a default user if no users are configured
    anyuser = app.db.users.find_one() # if no users this will == None
    if anyuser == None:
        password = pbkdf2_sha256.hash("removethisdefault")
        default = {
            "_id": uuid.uuid4().hex,
            "email":"default@netadept.remove",
            "username": "default",
            "password":password,
        }
        app.db.users.insert_one(default)
        app.db.authed_users.insert_one({'email': "default@netadept.remove"})

    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        pre_password = request.form.get("password")
        password = pbkdf2_sha256.hash(pre_password) # hash the password before saving in db
        #shortdate = datetime.datetime.today().strftime("%d-%m-%Y")

        usr = {
            "_id": uuid.uuid4().hex,
            "email":email,
            "username": username,
            "password":password,
        } # template for user data in db

        authmail = []
        aut = app.db.authed_users.find() 
        for ats in aut:
            amail = ats["email"]
            print(f"this is {amail}")
            authmail.extend([f"{amail}"]) # .extend used cos .append creats list inside a list

        if app.db.users.find_one({'username': usr["username"]}) or app.db.users.find_one({'email': usr["email"]}): # checks if username or email already in db
            flash("User or email already registered. Go to Login screen to continue")
            print("User or email already registered. Go to Login screen to continue")
            return render_template("register.html") 
        
        elif email not in authmail:
            print(type(email))
            print(type(authmail))
            flash("User not authorized. Please contact admin to whitelist email address")
            return render_template("register.html") 

        else:
            print(f"Username: {username} has been created and added to database")
            app.db.users.insert_one(usr) # adding the usr dict from above to db as per sign in form
            return redirect(url_for('login'))
    else:
        return render_template("register.html") 

# Login
@app.route("/login/", methods=["POST", "GET"])
def login():
    session["singleselect"] = "NONE"
    session["groupselectOne"] = "NONE" 
    session["groupselectTwo"] = "NONE"
    if request.method == "POST":
        username = request.form.get("username")
        pre_password = request.form.get("password")
        password = pbkdf2_sha256.hash(pre_password) 

        usr = {
            "_id": uuid.uuid4().hex,
            "username": username,
            "password":password,
        } 
        if app.db.users.find_one({'username': usr["username"]}):
            db_entry = app.db.users.find_one({'username': usr["username"]}) # Selects the correct collection from mongodb
            db_hash = db_entry["password"]
            pw_check = pbkdf2_sha256.verify(pre_password, db_hash) # check hashing the pre_password matches the hashe pw in the db (returns True/False)
            if app.db.users.find_one({'username': usr["username"]}) and pw_check: # checks if username and email already in db
                print(pw_check)
                session["username"] = username # Add session for username

                # Gets netAdept local server IP address
                #content = subprocess.run([f"curl ifconfig.me",], capture_output=True, text=True, shell=True)
                content = subprocess.run([f"dig +short myip.opendns.com @resolver1.opendns.com",], capture_output=True, text=True, shell=True)
                #tresults = content.stdout
                #svr_ip = tresults.replace('\n', '<br>')
                svr_ip = content.stdout
                session["svr_ip"] = svr_ip
                return redirect(url_for("dash"))

                #return render_template("dash.html", username=username)   
            else:
                print('no match')
                return render_template("login.html")         
        else:
            return render_template("login.html") 
    else:
        return render_template("login.html") 

# Logout
@app.route("/about/")
@login_required
def about():      
    return render_template("about.html")   

# Logout
@app.route("/logout/", methods=["POST", "GET"])
@login_required
def logout():
    if request.method == "POST":
        session.pop("username", None) # removes the group sessions if you select a host
        return render_template("login.html")        
    else:
        #session.pop("username", None) # removes the group sessions if you select a host
        return render_template("logout_confirm.html")          


@app.route("/logout_confirm/", methods=["POST", "GET"])
@login_required
def logout_confirm():
    session.pop("username", None) 
    return render_template("login.html")     

##### MongoDB Local #####

#client = MongoClient('localhost', 27017, username='root', password='netadept')
#app.db = client.netadeptdb
#hostinfo = app.db.hostgrps
#authdusr = app.db.authed_users


### Authorise Users ###

@app.route("/authed_users/", methods=["POST", "GET"])
@login_required
def authed_users():
    # Create empty lists so that there wont be an error if the DB is empty
    data = []
    headings = []
    
    auths = authdusr.find() 
    for ats in auths:
        authed = ats["email"]
        headings = ["Email Address", "Delete"]
        data.append([f"{authed}"])

    if request.method == "POST":
        email = request.form.get("email")
        #username = request.form.get("username")

        usr_auth = {
            "_id": uuid.uuid4().hex,
            "email":email,
        } # template for user data in db

        if app.db.authed_users.find_one({'email': usr_auth["email"]}): # checks if username or email already in db
            flash("User or email already Authorised")
            return render_template("authed_users.html", headings=headings, data=data) 
        else:
            print(f"User email: {email} has been Authorised")
            app.db.authed_users.insert_one(usr_auth) # adding the usr dict from above to db as per sign in form
        return render_template("authed_users.html", headings=headings, data=data) 
    else:
        return render_template("authed_users.html", headings=headings, data=data) 

@app.route("/del_auth/<devicename>", methods=["POST", "GET"])
@login_required
def del_auth(devicename):
    print(devicename)
    return render_template("del_auth.html", devicename=devicename) 

@app.route("/remove_auth/<devicename>", methods=["POST", "GET"])
@login_required
def remove_auth(devicename):
    print(devicename)
    app.db.authed_users.delete_one({'email': f"{devicename}"})
    app.db.users.delete_one({'email': f"{devicename}"})
    return redirect(url_for("authed_users"))

@app.route("/dash/", methods=["POST", "GET"])
@login_required
def dash():
    data_up = []
    data_down = []
    headings = []
    probes = {}
    headings = [" ", "Device", "  STATUS "]
    devicelist = nr.inventory.hosts
    connected_ips = {request.remote_addr}
    netadept_ip = {request.host}

    for dv in devicelist:
        dip = nr.inventory.hosts[f"{dv}"].hostname
        response = os.system(f'ping -c 1 {dip} -W .7')
        if response == 0:
            probes.update({f"{dv}": "UP"})
            data_up.append([f"{dv}", "UP"])
        else:
            probes.update({f"{dv}": "DOWN"})
            data_down.append([f"{dv}", "DOWN"])

    probes.pop("NONE")
    data_down.pop(0)
    upcount = (len(data_up))
    downcount = (len(data_down))
    return render_template("dash.html", probes=probes, headings=headings, data_up=data_up, data_down=data_down, 
                           upcount=upcount, downcount=downcount, connected_ips=connected_ips, netadept_ip=netadept_ip, current_user=current_user)  

 ### Home ###
    
@app.route("/dashboard/", methods=["POST", "GET"])
@login_required
def homepage():
#    print([t for t in app.db.users.find({})])
    if request.method == "POST":
        email = request.form.get("email")
#        print(f"this is the email: {email}")
        username = request.form.get("username")
        pre_password = request.form.get("password")
        password = pbkdf2_sha256.hash(pre_password) # hash the password before saving in db
        shortdate = datetime.datetime.today().strftime("%d-%m-%Y")

        usr = {
            "_id": uuid.uuid4().hex,
            "email":email,
            "username": username,
            "password":password,
        } # template for user data in db

        if app.db.users.find_one({'username': usr["username"]}) or app.db.users.find_one({'email': usr["email"]}): # checks if username or email already in db
            print("User or email already registered. Go to Login screen to continue")
        else:
            print(f"Username: {username} has been created and added to database")
            app.db.users.insert_one(usr) # adding the usr dict from above to db as per sign in form

        #if email not in app.db.users.find_one():
        #    app.db.users.insert_one({"email": email, "username": username, "password": password, "date": shortdate}) # add to "users" collection
        #    flash("New user added!")
        #else:
        #    flash("User already registered!")
#        app.db.users.insert_one({"email": email, "username": username, "password": password, "date": shortdate}) # add to "users" collection
#        print(app.db.list_collection_names()) # print colelctions
        print(app.db.users.find_one({'username': f'{username}'})) # print the first {'username': 'africasean'} match in a db
        pw_check = pbkdf2_sha256.verify(pre_password, password) # check hashing the pre_password matches the hashe pw in the db (returns True/False)
        if pw_check: 
            print(pw_check)
        else:
            print('no match')

        return render_template("dashboard.html", hostlist=hostlist)  
    else:
        return render_template("dashboard.html", hostlist=hostlist)   

### Reload Flask Inventory ###

def get_nornir():
    """Reinitialize Nornir with updated inventory."""
    return InitNornir(
        inventory={
            "options": {
                "host_file": f"{home}/netadept/inventory/hosts.yaml",
                "group_file": f"{home}/netadept/inventory/groups.yaml",
                "defaults_file": f"{home}/netadept/inventory/defaults.yaml",
            }
        }
    )


#@app.route("/reload_inventory")
#def reload_inventory():
#    """Endpoint to reload the Nornir inventory."""
#    try:
#        nr = get_nornir()
#        hosts = list(nr.inventory.hosts.keys())
#        allhosts.clear()
#        for dvcs in hosts:
#            allhosts.append(dvcs)
#            print(allhosts)
#
#        return redirect(url_for("inventory"))
#        #return jsonify({
#        #    "status": "success",
#        #    "hosts": list(nr.inventory.hosts.keys()),
#        #    "groups": list(nr.inventory.groups.keys())
#        #})
#    except Exception as e:
#        return jsonify({"status": "error", "message": str(e)}), 500   


#########################################################################################################

##### Device Selector #####

@app.route("/deviceselector", methods=["POST", "GET"])
@login_required
def deviceselector():
    allhosts = []

    nr = get_nornir()
    hostlist = list(nr.inventory.hosts.keys())

    if request.method == "POST":
        session.pop("groupselectOne", None) # removes the group sessions if you select a host
        session.pop("groupselectTwo", None)
        session["groupselectOne"] = "NONE" # Assign "ALL" value to groupselectOne
        session["groupselectTwo"] = "NONE"
        singleselect = request.form["singleselect"] 
        session["singleselect"] = singleselect 

        singleselect = session["singleselect"]
        device_ip = nr.inventory.hosts[f"{singleselect}"].hostname
        single_host = nr.filter(hostname=device_ip)
        device_list=single_host.inventory.hosts.values()
        print(device_list)
        print(allhosts)
        return render_template("deviceselector.html", hostlist=hostlist, device_list=device_list, allhosts=allhosts) 
    else:
        return render_template("deviceselector.html", hostlist=hostlist) #, device_list=device_list)   
        #return render_template('error.html'), 404

##### Group Selector #####

@app.route("/groupselector", methods=["POST", "GET"])
@login_required
def groupselector():
    
    nr = get_nornir()
    grouplist=nr.inventory.groups.values()
    
    if request.method == "POST":
        session.pop("singleselect", None) # removes the device sessions if you select a group
        session["singleselect"] = "NONE"
        groupselectOne = request.form["groupselectOne"] 
        session["groupselectOne"] = groupselectOne 
        groupselectTwo = request.form["groupselectTwo"] 
        session["groupselectTwo"] = groupselectTwo 

        groupselectOne = session["groupselectOne"]
        groupselectTwo = session["groupselectTwo"]
        group_devices = nr.filter(F(groups__contains=groupselectOne) & F(groups__contains=groupselectTwo))
        device_list=group_devices.inventory.hosts.values()

        return render_template("groupselector.html", grouplist=grouplist, device_list=device_list)  
    return render_template("groupselector.html", grouplist=grouplist) 
	
#########################################################################################################

##### Troubleshooting ##### 

@app.route("/ping/", methods=["POST", "GET"])
@login_required
def ping():
    if request.method == "GET":
        svr_ip = session["svr_ip"]
        singleselect = session["singleselect"]
        groupselectOne = session["groupselectOne"] 
        groupselectTwo = session["groupselectTwo"] 
        
        device_ip = nr.inventory.hosts[f"{singleselect}"].hostname
        content = subprocess.run([f"ping {device_ip} -c 4",], capture_output=True, text=True, shell=True)
        tresults = content.stdout
        results = tresults.replace('\n', '<br>')
        return render_template("ping.html", hostlist=hostlist, results=results, device_ip=device_ip) 
    else:
        return render_template("ping.html", hostlist=hostlist)    
    
@app.route("/tracepath/", methods=["POST", "GET"])
@login_required
def tracepath():
    if request.method == "GET":
        singleselect = session["singleselect"]
        device_ip = nr.inventory.hosts[f"{singleselect}"].hostname
        content = subprocess.run([f"tracepath {device_ip} -m 8 -b",], capture_output=True, text=True, shell=True)
        tresults = content.stdout
        results = tresults.replace('\n', '<br>')
        return render_template("tracepath.html", hostlist=hostlist, content=content, results=results, device_ip=device_ip) 
    else:
        return render_template("tracepath.html", hostlist=hostlist) 

@app.route("/mon_mong_draw/", methods=["POST", "GET"])
@login_required
def mon_mong_draw():
    ipandport = {request.host}      # get browser ip and port
    ippstr = (str(ipandport))       # convert to string
    ippsplt = ippstr.split(":")[0]  # split at :
    iponly = ippsplt.strip("'{")    # strip '{

    return render_template("mon_mong_draw.html", iponly=iponly) 


@app.route("/nslookup/", methods=["POST", "GET"])
@login_required
def nslookup():
    if request.method == "POST":
        ipadd = request.form["ipadd"] 
        session["ipadd"] = ipadd 
        ipadd = session["ipadd"]

        content = subprocess.run([f"nslookup {ipadd}",], capture_output=True, text=True, shell=True)
        results = content.stdout
        return render_template("nslookup.html", results=results) 
    else:
        return render_template("nslookup.html") 

@app.route("/reverse_dns/", methods=["POST", "GET"])
@login_required
def reverse_dns():
    if request.method == "POST":
        address = request.form["address"] 
        session["address"] = address 
        address = session["address"]

        print(f"{address}")

        #content = subprocess.run([f"dig -x  {address}",], capture_output=True, text=True, shell=True)
        content = subprocess.run(["python", "scripts/reverse_dns.py", f"{address}"], capture_output=True, text=True)
        tresults = content.stdout
        results = tresults.replace('\n', '<br>')
        return render_template("reverse_dns.html", results=results) 
    return render_template("reverse_dns.html") 
    
@app.route("/domain/", methods=["POST", "GET"])
@login_required
def domain():
    if request.method == "POST":
        domain = request.form["domain"] 
        session["domain"] = domain 
        domain = session["domain"]

        print(domain)

        content = subprocess.run(["python", "scripts/who.py", f"{domain}"], capture_output=True, text=True)
        tresults = content.stdout
        results = tresults.replace('\n', '<br>')
        return render_template("whois.html", results=results) 
    return render_template("whois.html") 

@app.route("/passgen/", methods=["POST", "GET"])
@login_required
def passgen():
    characterList = ""
    password = []
    if request.method == "POST":
        len = request.form["length"] 
        length = int(len)
        selected_subjects = request.form.getlist('passgen')
        for abc in selected_subjects:
            if abc == 'letters':
                characterList += string.ascii_letters
            if abc == 'digits':
                characterList += string.digits
            if abc == 'punctuation':
                characterList += string.punctuation

        for i in range(length):
            randomchar = random.choice(characterList)
            password.append(randomchar)
        pw = "".join(password)
        return render_template("passgen.html", password=password, pw=pw) 
    return render_template("passgen.html") 

@app.route("/netwkcalc/", methods=["POST", "GET"])
@login_required
def netwkcalc():
    if request.method == "POST":
        ip_cidr = request.form["netwrk"] 
        network = ipaddress.IPv4Network(ip_cidr, strict=False)

        Network_Address = f"{network.network_address}"
        Broadcast_Address = f"{network.broadcast_address}"
        Subnet_Mask = f"{network.netmask}"
        Total_Hosts = f"{network.num_addresses}"
        Usable_Hosts = f"{network.num_addresses - 2}"
        First_Usable_IP = f"{network.network_address + 1}"
        Last_Usable_IP = f"{network.broadcast_address - 1}"

        return render_template("netwkcalc.html", Network_Address=Network_Address, Broadcast_Address=Broadcast_Address, Subnet_Mask=Subnet_Mask,
                                Total_Hosts=Total_Hosts, Usable_Hosts=Usable_Hosts, First_Usable_IP=First_Usable_IP,
                               Last_Usable_IP=Last_Usable_IP, ip_cidr=ip_cidr)     
    return render_template("netwkcalc.html") 

@app.route("/cli/", methods=["POST", "GET"])
@login_required
def cli():
    ipandport = {request.host}      # get browser ip and port
    ippstr = (str(ipandport))       # convert to string
    ippsplt = ippstr.split(":")[0]  # split at :
    iponly = ippsplt.strip("'{")    # strip '{
    print(iponly)

    if request.method == "POST":
        port = request.form["port"] 
        session["port"] = port 
        port = session["port"]

        singleselect = session["singleselect"]
        device_ip = nr.inventory.hosts[f"{singleselect}"].hostname
        platform = nr.inventory.hosts[f"{singleselect}"].platform
        if platform == 'fortinet':
            content = subprocess.Popen([f"gotty --port {port} --permit-write ssh admin@{device_ip}",], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            #content = subprocess.run([f"gotty --port {port} --permit-write ssh sbrown@{device_ip}",], capture_output=True, text=True, shell=True)
            content = subprocess.Popen([f"gotty --port {port} --permit-write ssh sbrown@{device_ip}",], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"Connecting to: http://{iponly}:{port}")
        terminal = f"http://{iponly}:{port}"
        print(terminal)
        return render_template("cli.html", hostlist=hostlist, device_ip=device_ip, terminal=terminal, iponly=iponly) 
    else:
        return render_template("cli.html", hostlist=hostlist)  

@app.route("/cli_tool/", methods=["POST", "GET"])
@login_required
def cli_tool():
    singleselect = session["singleselect"]

    device_ip = nr.inventory.hosts[f"{singleselect}"].hostname
    single_host = nr.filter(hostname=device_ip)

    if request.method == "POST":
        cmd1 = request.form.get("cmd1")
        cmd2 = request.form.get("cmd2")
        cmd3 = request.form.get("cmd3")
        cmd4 = request.form.get("cmd4")
        cmd5 = request.form.get("cmd5")
        cmd6 = request.form.get("cmd6")
        cmd7 = request.form.get("cmd7")
        cmd = [cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7 ]

        cli_dir = f"{home}/netadept/flask/cli" 
        cli_outputfile = f"{home}/netadept/flask/cli/cli_out.txt" 

        pathlib.Path(cli_dir).mkdir(exist_ok=True) 


        with open(f"{cli_dir}" + "/cli_cmds.txt", "w") as f: 
            for cmds in cmd:
                f.write(cmds + "\n")
            f.close()

        result = subprocess.run(["python", "scripts/cli_tool.py", f"{device_ip}"], capture_output=True, text=True) 


        try:
            with open(f"{cli_outputfile}", "r") as file:
                out = file.read()
                content = out.replace('\n', '<br>')
                return render_template("cli_tool.html", hostlist=hostlist, content=content)
            
        except FileNotFoundError:
            print("File does not exist.")
            return redirect(url_for("unreachable")) # change this to an error page that flashes the error


        return render_template('cli_tool.html', singleselect=singleselect, result=result)
    return render_template('cli_tool.html', singleselect=singleselect)

@app.route("/fortinet/", methods=["POST", "GET"])
@login_required
def fortinet():
    singleselect = session["singleselect"]
    device_ip = nr.inventory.hosts[f"{singleselect}"].hostname
    platform = nr.inventory.hosts[f"{singleselect}"].platform
    if request.method == "POST":
        return render_template("fortinet.html", hostlist=hostlist, device_ip=device_ip, platform=platform) 
    else:
        return render_template("fortinet.html", hostlist=hostlist,device_ip=device_ip, platform=platform)   

####################################################################################################################################

##### Test #####

@app.route("/navbar/") # POST Method removed as not required
@login_required
def navbar():
    return render_template("navbar.html")

@app.route("/empty/") # POST Method removed as not required
@login_required
def empty():
    results = request.form
    singleselect = session["singleselect"]
    return render_template("empty.html", hostlist=hostlist, singleselect=singleselect)

@app.route("/config_runt/", methods=["POST", "GET"])
@login_required
def config_runt():
    if request.method == "POST":
        singleselect = session["singleselect"] # imports session from device selector
        device_ip = nr.inventory.hosts[f"{singleselect}"].hostname  # selects the ip address in the inventory host.yaml
        part = request.form["part"] 
        print(f'session is : {part} !!!!')
        session["part"] = part 
        device = nr.inventory.hosts[f"{singleselect}"] # selects the device in the inventory host.yaml
        output = subprocess.run(["python", "scripts/config_part.py", f"{device_ip}", f"{part}"], capture_output=True, text=True) # runs subprocess to access the cli and argpases the ip adress as a variable to select the device to run the script against
        tresults = output.stdout # raw output
        presults = tresults.replace('\n', '<br>') # turn into a list and swap \n qith <br> for the html
        results = presults[550:-113] # cut the first few lines of of the output to make it look neater

        with open(f"{home}/netadept/flask/scripts/interfaces/interfaces", "r") as f:
            intfcs = f.read().splitlines()
            print(intfcs)
        return render_template("config_runint.html", hostlist=hostlist, results=results, intfcs=intfcs)
    
    elif request.method == "GET":
        singleselect = session["singleselect"] # imports session from device selector
        device_ip = nr.inventory.hosts[f"{singleselect}"].hostname  # selects the ip address in the inventory host.yaml
        output = subprocess.run(["python", "scripts/interfaces/int_show_run.py", f"{device_ip}"], capture_output=True, text=True) 
        tresults = output.stdout # raw output
        gresults = tresults.replace('\n', '<br>') # turn into a list and swap \n qith <br> for the html
        shresults = gresults.replace('[0m', ' ')

        with open(f"{home}/netadept/flask/scripts/interfaces/interfaces", "r") as f:
            intfcs = f.read().splitlines()
            print(intfcs)

        repattern = re.compile("(?<=beginnig).*?(?=ending)", flags=re.I | re.M)
        reresult = repattern.findall(shresults)
        return render_template("config_runint.html", hostlist=hostlist, shresults=shresults, intfcs=intfcs, reresult=reresult)

### Master Show Script ###

@app.route("/show/<show_command>/", methods=["POST", "GET"])
@login_required
def show(show_command):
    # Redirects to the Device Selector page if all sellections == 'NONE'
    if session["singleselect"] == "NONE" and session["groupselectOne"] == "NONE" and session["groupselectTwo"] == "NONE":
        print("No sessions selected")
        return redirect(url_for("deviceselector"))
    
    singleselect = session["singleselect"]
    groupselectOne = session["groupselectOne"] 
    groupselectTwo = session["groupselectTwo"] 

    device_ip = nr.inventory.hosts[f"{singleselect}"].hostname 
    device = nr.inventory.hosts[f"{singleselect}"] 
    platform = nr.inventory.hosts[f"{singleselect}"].platform

    if show_command == "show_int":
        output = subprocess.run(["python", "scripts/int_show.py", f"{device_ip}", f"{groupselectOne}", f"{groupselectTwo}", f"{show_command}"], capture_output=True, text=True) 
    else:
        print(f"Show Script is running for: {platform}")
        output = subprocess.run(["python", "scripts/show.py", f"{device_ip}", f"{groupselectOne}", f"{groupselectTwo}", f"{show_command}"], capture_output=True, text=True) 

    output_dir = f"{home}/netadept/flask/output"
    groupfile=str(output_dir) + "/" + "output.txt"

    try:
        with open(f"{groupfile}", "r") as file:
            out = file.read()
            content = out.replace('\n', '<br>')
            return render_template("config.html", hostlist=hostlist, content=content, show_command=show_command)
    except FileNotFoundError:
        print("File does not exist.")
        return redirect(url_for("unreachable")) # change this to an error page that flashes the error
    return render_template("config.html", hostlist=hostlist)

@app.route("/unreachable/") # POST Method removed as not required
@login_required
def unreachable():
    return render_template("unreachable.html")

### Inventory hostfile configuration ###

@app.route("/inventory/", methods=["POST", "GET"])
@login_required
def inventory():
    # Create empty lists so that there wont be an error if the DB is empty
    data = []
    headings = []

    nr = get_nornir()
    grouplist=nr.inventory.groups.values()
    
    hosts = hostinfo.find() #  find all the entries in the hostinfo DB and assign to "hosts"
    for hsts in hosts:
        dvc = hsts['device']
        ipadd = hsts['ip']
        platfrm = hsts['platform']
        prt = hsts['port']
        grp1 = hsts['group1']
        grp2 = hsts['group2']
        grp3 = hsts['group3']
        grp4 = hsts['group4']
        grp5 = hsts['group5']

        headings = ["Device", "IP Address", "Platform", "Port", "Group1", "Group2", "Group3", "Group4", "Group5", "Delete"]
        data.append([f"{dvc}", f"{ipadd}", f"{platfrm}", f"{prt}", f"{grp1}", f"{grp2}", f"{grp3}", f"{grp4}", f"{grp5}"])

    if request.method == "POST":
        device = request.form.get("device")
        ip = request.form.get("ip")
        platform = request.form.get("platform")
        port = request.form.get("port")
        group1 = request.form.get("group1")
        group2 = request.form.get("group2")
        group3 = request.form.get("group3")
        group4 = request.form.get("group4")
        group5 = request.form.get("group5")
        snmpver = request.form.get("snmpver")
        snmpcom = request.form.get("snmpcom")
        snmpgrp = request.form.get("snmpgrp")

        inventory_hosts = {
            "_id": uuid.uuid4().hex,
            "device":device,
            "ip": ip,
            "platform":platform,
            "port": port,
            "group1": group1,
            "group2": group2,
            "group3": group3,
            "group4": group4,
            "group5": group5,
            "snmpver": snmpver,
            "snmpcom": snmpcom,
            "snmpgrp": snmpgrp,
        }
        if request.form.get("device"):
            print(f"This is the device: {device}")
            if app.db.hostgrps.find_one({'device': f"{device}"}):
                print(f"Device with name: {device} is already in use, please select a new device name")
                return render_template("inventory.html", headings=headings, data=data, grouplist=grouplist)
            else:
                print(f"device: {device} has been created and added to database")
                app.db.hostgrps.insert_one(inventory_hosts) 
            return render_template("inventory.html", headings=headings, data=data, grouplist=grouplist)
        elif request.form.get("device_edit"):
            print("editing")
    else:
        return render_template("inventory.html", headings=headings, data=data, grouplist=grouplist) 

@app.route("/del_select/<devicename>", methods=["POST", "GET"])
@login_required
def del_select(devicename):
    ipandport = {request.host}      # get browser ip and port
    ippstr = (str(ipandport))       # convert to string
    ippsplt = ippstr.split(":")[0]  # split at :
    iponly = ippsplt.strip("'{")    # strip '{
    print(iponly)
    print(devicename)
    return render_template("del_select.html", devicename=devicename, iponly=iponly) 

@app.route("/delete/<devicename>", methods=["POST", "GET"])
@login_required
def delete(devicename):
    print(devicename)
    app.db.hostgrps.delete_one({'device': f"{devicename}"})
    return redirect(url_for("inventory"))


### Write hosts to yaml file ###

host_tmplt = Template(
'''
{{dvc}}:
  hostname: {{ipadd}}
  platform: {{platfrm}}
  port: {{prt}}
  groups:
    - {{grp1}}
    - {{grp2}}
    - {{grp3}}
    - {{grp4}}
    - {{grp5}}
    - {{grp0}}
  data:
    ver: {{snmpver}}
    comm: {{snmpcom}}
    grp: {{snmpgrp}}

''')

### update hosts.yml ###
@app.route("/update_hostfile/", methods=["POST", "GET"])
@login_required
def update_hostfile():
    output_folder = f"{home}/netadept/inventory"
    with open(output_folder + "/hosts.yaml", "w") as f:
        print("hosts.yaml has been cleared")
        print(grouplist)
        print(hostlist)
        f.write("--- \n\nNONE: # Empty group for filtering \n  hostname: \n ")

        
    hosts = hostinfo.find() #  find all the entries in the hostinfo DB and assign to "hosts"
    for hsts in hosts:
        dvc = hsts['device']
        ipadd = hsts['ip']
        platfrm = hsts['platform']
        prt = hsts['port']
        grp1 = hsts['group1']
        grp2 = hsts['group2']
        grp3 = hsts['group3']
        grp4 = hsts['group4']
        grp5 = hsts['group5']
        grp0 = 'ALL'
        snmpver = hsts['snmpver']
        snmpcom = hsts['snmpcom']
        snmpgrp = hsts['snmpgrp']

        template_output = host_tmplt.render(dvc=dvc, ipadd=ipadd, platfrm=platfrm, prt=prt, grp1=grp1, grp2=grp2, grp3=grp3, grp4=grp4, grp5=grp5, grp0=grp0, snmpver=snmpver, snmpcom=snmpcom, snmpgrp=snmpgrp)

        with open(output_folder + "/hosts.yaml", "a") as f:
            f.write(template_output)


    output = subprocess.run(["python", "scripts/zabbix.py"], capture_output=True, text=True)

    return redirect(url_for("inventory"))

@app.route("/edit_file/", methods=["POST", "GET"])
@login_required
def edit_file():
    output_folder = '/home/netadept/netadept/inventory'
    file_path = (output_folder + "/groups.yaml")  # Path to your text file
    content = ''
    if request.method == 'POST':
        content = request.form['text']
        with open(file_path, 'w') as f:
            f.write(content)
    else:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
    return render_template('edit_groups_file.html', content=content)

@app.route("/hosts_viewer/", methods=["GET"])
@login_required
def hosts_viewer():
    output_folder = '/home/netadept/netadept/inventory'
    file_path = (output_folder + "/hosts.yaml")  # Path to your text file
    content = ''
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
    return render_template('hosts_viewer.html', content=content)

#########################################################################################################

@app.route('/backups/', methods = ['POST', "GET"])  
@login_required
def backups():  
    ipandport = {request.host}      # get browser ip and port
    ippstr = (str(ipandport))       # convert to string
    ippsplt = ippstr.split(":")[0]  # split at :
    iponly = ippsplt.strip("'{")    # strip '{
    print(iponly)


    data = []
    headings = []
    singleselect = session["singleselect"]
    backup_folder = f"{home}/netadept/flask/backups/{singleselect}/"
    app.config['backup_folder'] = backup_folder


    for root, dirs, files in os.walk(f'{backup_folder}'):
        #print(f"Files: {files}")
        for fls in files:
            headings = ["Backup Files", "Delete", "Download"]
            data.append([f"{fls}"])

    if request.method == 'POST':  
        file = request.files['file']
        if file.filename != '':
            file.save(os.path.join(app.config['backup_folder'], secure_filename(file.filename)))
            return render_template("backup.html", headings=headings, data=data, name = file.filename, singleselect=singleselect) 
    else:
        return render_template("backup.html", headings=headings, data=data, singleselect=singleselect) # files=files,

@app.route("/delete_backups/<filename>", methods=["POST", "GET"])
@login_required
def delete_backups(filename):
    singleselect = session["singleselect"]
    backup_folder = f"{home}/netadept/flask/backups/{singleselect}/"
    app.config['backup_folder'] = backup_folder

    filepath = (f'{backup_folder}' + f'{filename}')
    if os.path.exists(filepath):
        #os.unlink(filepath)
        os.remove(filepath)
        return redirect(url_for("backups"))
    else:
        print(f'The file "{filepath}" does not exist.')
        return redirect(url_for("backups"))       

@app.route('/download_backups/<filename>')
@login_required
def download_backups(filename):
    singleselect = session["singleselect"]
    backup_folder = f"{home}/netadept/flask/backups/{singleselect}/"
    app.config['backup_folder'] = backup_folder

    filepath = (f'{backup_folder}' + f'{filename}')
    return send_file(filepath, as_attachment=True)

#########################################################################################################

cron = CronTab(user=f"{current_user}")

@app.route("/backup_cron/")
def backup_cron():
    job = cron.new(command="./backupscript.sh")
    job.setall('30 6 * * *')

    cron.remove_all(command="./backupscript.sh")
    cron.write()

    return redirect(url_for("backup"))

@app.route('/schedule/', methods = ['POST', "GET"])
def schedule():
    #cron = CronTab(user=f"{current_user}")
    job = cron.new(command="./backupscript.sh")
    if request.method == 'POST':
        min = request.form.get("min")
        hrs = request.form.get("hrs")
        day = request.form.get("day")
        mth = request.form.get("mth")
        dow = request.form.get("dow")

        config = request.form.get("config")
        ints = request.form.get("ints")
        routing = request.form.get("routing")
        logs = request.form.get("logs")

        job.setall(f"{min} {hrs} {day} {mth} {dow}")
        cron.write()

        return render_template("schedule.html")
    return render_template("schedule.html")

@app.route('/clear/', methods = ['POST', "GET"])
def clear():
    #cron = CronTab(user=f"{current_user}")
    cron.remove_all(command="./backupscript.sh")
    cron.write()
    return redirect(url_for("schedule"))

@app.route('/show_bkps/', methods = ['POST', "GET"])
def show_bkps():
    #cron = CronTab(user=f"{current_user}")
    data = []
    headings = []

    for job in cron:
        data.append(job)
        
    headings = ["Minute", "Hour of the Day", "Day", "Month", "Day of the Week"]

    return render_template("show_bkps.html", data=data, headings=headings)

#########################################################################################################


upload_folder = f"{home}/netadept/flask/files/"
app.config['upload_folder'] = upload_folder

@app.route('/upload/', methods = ['POST', "GET"])  
@login_required
def upload():  
    singleselect = session["singleselect"]
    data = []
    headings = []

    for root, dirs, files in os.walk(f'{upload_folder}'):
        print(f"Files: {files}")
        for fls in files:
            headings = ["Files on netAdept", "Del", "Download", "Push"]
            data.append([f"{fls}"])

    if request.method == 'POST':  
        file = request.files['file']
        if file.filename != '':
            file.save(os.path.join(app.config['upload_folder'], secure_filename(file.filename)))
            return render_template("upload.html", headings=headings, data=data, name = file.filename, singleselect=singleselect) 
    else:
        return render_template("upload.html", files=files, headings=headings, data=data, singleselect=singleselect)

@app.route("/delete_files_select/<filename>", methods=["POST", "GET"])
@login_required
def delete_files_select(filename):
    return render_template("delete_files_select.html", filename=filename) 

@app.route("/delete_files/<filename>", methods=["POST", "GET"])
@login_required
def delete_files(filename):
    filepath = (f'{upload_folder}' + f'{filename}')
    if os.path.exists(filepath):
        #os.unlink(filepath)
        os.remove(filepath)
        return redirect(url_for("upload"))
    else:
        print(f'The file "{filepath}" does not exist.')
        return redirect(url_for("upload"))       

@app.route('/download/<filename>')
@login_required
def download(filename):
    filepath = (f'{upload_folder}' + f'{filename}')
    return send_file(filepath, as_attachment=True)

@app.route('/download_output/')
@login_required
def download_output():
    filepath = f"{home}/netadept/flask/output/output.txt"
    return send_file(filepath, as_attachment=True)

@app.route('/download_clioutput/')
@login_required
def download_clioutput():
    filepath = f"{home}/netadept/flask/cli/cli_out.txt" 
    return send_file(filepath, as_attachment=True)

@app.route("/filesend_confirm/<filename>", methods=["POST", "GET"])
@login_required
def filesend_confirm(filename):
    if session["singleselect"] == "NONE" and session["groupselectOne"] == "NONE" and session["groupselectTwo"] == "NONE":
        print("No sessions selected")
        return redirect(url_for("deviceselector"))

    return render_template("filesend_confirm.html", filename=filename) 

@app.route('/filesend/<filename>')
@login_required
def filesend(filename):
    singleselect = session["singleselect"]
    groupselectOne = session["groupselectOne"] 
    groupselectTwo = session["groupselectTwo"] 
    device_ip = nr.inventory.hosts[f"{singleselect}"].hostname 

    output = subprocess.run(["python", "scripts/file_transfer.py", f"{device_ip}", f"{groupselectOne}", f"{groupselectTwo}", f"{filename}"], capture_output=True, text=True)
    return redirect(url_for("upload"))


### Upload a file from selected device ###

dirlist = []
@app.route('/filefromdevice/')
@login_required
def filefromdevice():
    if session["singleselect"] == "NONE" and session["groupselectOne"] == "NONE" and session["groupselectTwo"] == "NONE":
        print("No sessions selected")
        return redirect(url_for("deviceselector"))

    data = []
    singleselect = session["singleselect"]
    headings = [f"Files on {singleselect}", "Upload"]
    device_ip = nr.inventory.hosts[f"{singleselect}"].hostname
    output = subprocess.run(["python", "scripts/filefromdevice.py", f"{device_ip}"], capture_output=True, text=True) 
    file_dir = f"{home}/netadept/flask"
    with open(f"{file_dir}" + "/dirfile.txt", "r") as f:
        content = f.readlines()
        data.append(content)
    if request.method == "POST":
        return render_template("filefromdevice.html", dirlist=dirlist, headings=headings, data=data) 
    return render_template("filefromdevice.html", dirlist=dirlist, headings=headings, data=data)

@app.route("/filereceive_confirm/<filename>", methods=["POST", "GET"])
@login_required
def filereceive_confirm(filename):
    return render_template("filereceive_confirm.html", filename=filename) 

@app.route('/filereceive/<filename>')
@login_required
def filereceive(filename):
    singleselect = session["singleselect"]
    device_ip = nr.inventory.hosts[f"{singleselect}"].hostname 
    filename = filename.strip('\n') # stripping the return value from the "filename" variable inherited from the file 
    output = subprocess.run(["python", "scripts/file_transfer_rx.py", f"{device_ip}", f"{filename}",], capture_output=True, text=True)
    print(output)
    return redirect(url_for("upload"))


flask_host="0.0.0.0"
flask_port="15000"

if __name__ == "__main__":
    app.run(host=flask_host, port=flask_port, debug=True)