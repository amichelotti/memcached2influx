import argparse
from influxdb import InfluxDBClient
from datetime import datetime
import sys  
from pymemcache.client import base
import os
import re
import json
import time

    
#Kiwi
def jsonKey2Influx(key, clientMemcached, name):
    data = clientMemcached.get(key)
    data = json.loads(data)
    payload = []
    payload.append({
        "measurement": name,
        "tags": {
            "key": key
        },
        "fields": data
    })
    return payload

def jsonData2Influx(fileData,clientMemcached):
    payload = []
    jsonData = clientMemcached.get(fileData['keybind'])
    fileData['memcached'] = json.loads(jsonData)
    
    if(fileData["variables"]):
        print(fileData['variables'])
        print(fileData['memcached'])
        print(type(fileData['memcached']))
    payload.append({
            "measurement": fileData["name"],
            "tags": {
                "key": fileData["keybind"]
            },
            "fields": fileData["memcached"]
    })
    return payload


def findTheKey(configFile):
    data = {}
    #find all the line with usefull data, except for keybind
    pattern = r'^"(.+)":(.+,(( ←)|[^a-zA-Z ]))'
    for line in configFile:
        match = re.search(pattern,line)
        #knowing that the keybind is always the last value, the return is set right after it
        if(match):
            #match = re.search(pattern,line)
            parameter = re.sub(r'(,|"|( ←))(?![^\[\]]*\])',"",match.group(2))
            data[match.group(1)] = parameter
        elif(line.find('keybind') != -1):
            line = re.sub(r',|( ←)',"",line)
            pattern = r'"(.+)":"(.+)"'
            match = re.search(pattern,line)
            data[match.group(1)] = match.group(2)
            data['name'] = data['name'][0:-1]
            return data
        

            

parser = argparse.ArgumentParser()

parser.add_argument("-u", "--username", required = False ,default="", help = "the username needed to log in the db")
parser.add_argument("-p", "--password", required = False ,default="", help = "the password needed to log in the db")
parser.add_argument("-s", "--server", required = False , default="", help = "the ip address of the server")
parser.add_argument("-d", "--database", required = False, default = "" , help = "the name of the database you want to log in")
parser.add_argument("-f", "--file",required = False, help = "the configuration file path")
parser.add_argument("-n", "--name",required = False, help = "if you're not using a configuration file, use this parameter to chose the name of the measurement")
parser.add_argument("-k", "--key",required = False, help = "the key needed to find the data in the memcached DB")
parser.add_argument("-po", "--port", help = "the port associated with the server address")
parser.add_argument("-r", "--rate", required = False, default = 5, help = "specify the seconds between 2 different push in the influx db, use this option only if you're not using a configuration file")


args = parser.parse_args()

#log in the influx DB
#python memcached2Influx.py -s vldantemon003.lnf.infn.it -po 8086 -f '/home/riccardo/Random bs go/Test/cofnigurationFile.txt' 
try:
    clientInflux = InfluxDBClient(host=args.server, port=args.port, username=args.username, password=args.password)
    clientInflux.switch_database("dcsMemDb")
    print("succesfully logged in\n")
except:
    sys.exit("Error: Invalid parameters, please try again")

#log in the memcached DB
#memcached_server = "192.168.198.20"
#mc_port = 11211
try:
    clientMemcached = base.Client( ("192.168.198.20" , 11211) , connect_timeout=20.0)
except:
    sys.exit('Cannot reach the memcached server, try again later')


if args.key:
    refreshRate = 5
    if type(args.rate) == 'int':
        refreshRate = args.rate
    while True:
        payload = []
        if args.name:
            payload = jsonKey2Influx(args.key, clientMemcached, args.name)
        else:
            payload = jsonKey2Influx(args.key, clientMemcached, args.key)
        print('Publishing data')
        print(payload)
        #clientInflux.write_points(payload)
        time.sleep(refreshRate)

elif args.file:
    try:
        open(args.file,'r')
    except FileNotFoundError as e:
        sys.exit("Error: " + args.iptable + " is not valid or does not point to a DBFile.")
    if os.path.isfile(args.file):
        with open(args.file,'r') as configFile:
            while (True):
                fileData = findTheKey(configFile)
                payload = []
                if fileData == None:
                    break
                if fileData["type"] == "json":  
                    payload = jsonData2Influx(fileData,clientMemcached)
                    print('Publishing into influx:')
                    print(payload)
                    print('\n')
                    #clientInflux.write_points(payload)