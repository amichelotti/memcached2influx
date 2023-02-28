import argparse
from influxdb import InfluxDBClient
from datetime import datetime
import sys
from pymemcache.client import base
import os
import re
import json

    
#dafneStat
def jsonData2Influx(fileData,clientMemcached):
    jsonData = clientMemcached.get(fileData['keybind'])
    fileData['memcached'] = json.loads(jsonData)
    payload = []
    fields = {}
    for field in fileData["memcached"]:
        fields [field] = fileData["memcached"][field]
    payload.append({
            "measurement": "dafneStat",
            "tags": {
                "key": fileData["keybind"]
            },
            "fields": fields
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
            parameter = re.sub(r',|"|( ←)',"",match.group(2))
            data[match.group(1)] = parameter
        elif(line.find('keybind') != -1):
            line = re.sub(r',|( ←)',"",line)
            pattern = r'"(.+)":"(.+)"'
            match = re.search(pattern,line)
            data[match.group(1)] = match.group(2)
            return data
        

            

parser = argparse.ArgumentParser()

parser.add_argument("-u", "--username", required = False ,default="", help = "the username needed to log in the db")
parser.add_argument("-p", "--password", required = False ,default="", help = "the password needed to log in the db")
parser.add_argument("-s", "--server", required = False , default="", help = "the ip address of the server")
parser.add_argument("-d", "--database", required = False, default = "" , help = "the name of the database you want to log in")
parser.add_argument("-f", "--file", default = "." , help = "the configuration file path")
parser.add_argument("-po", "--port", help = "the port associated with the server address")

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
    
try:
    if os.path.isfile(args.file):
        with open(args.file,'r') as configFile:
            while (True):
                fileData = findTheKey(configFile)
                payload = []
                print (type(fileData))
                if fileData == None:
                    break
                if fileData["type"] == "json":
                    payload = jsonData2Influx(fileData,clientMemcached)
                    print (payload)
                    clientInflux.write_points(payload)
except FileNotFoundError as e:
    sys.exit("Error: " + args.iptable + " is not valid or does not point to a DBFile.")
print("program ended succesfully")