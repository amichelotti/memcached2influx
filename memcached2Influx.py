import argparse
from influxdb import InfluxDBClient
from datetime import datetime
import sys  
from pymemcache.client import base
import os
import re
import json
import time

    
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
    memcached = json.loads(jsonData)
    fileData["rate"] = 5
    fileData["currentTime"] = 0.0
    
    payload.append({
            "measurement": fileData["name"],
            "tags": {
                "key": fileData["keybind"]
            },
            "fields": memcached,
            "parameter":fileData
    })
    return payload

def byteData2Influx(fileData,clientMemcached):
    payload = []
    byteArray = clientMemcached.get(fileData['keybind'])
    memcached =byteArray[int(fileData['offset'])]
    fileData["currentTime"] = 0.0
    try:
        fileData["rate"] = int(fileData["rate"])
    except:
        fileData["rate"] = 5
    
    payload.append({
            "measurement": fileData["name"],
            "tags": {
                "key": fileData["keybind"]
            },
            "fields": {
                fileData["name"] : memcached
                },
            "parameter" : fileData
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
            parameter = re.sub(r'(,|"|( ←)|\n)(?![^\[\]]*\])',"",match.group(2))
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
parser.add_argument("-is", "--influxServer",required = True, help = "the address of the influx server")
parser.add_argument("-id", "--influxDatabase", required = True, help = "the name of the database you want to log in")
parser.add_argument("-ip", "--influxPort",required = False, default = 8086, help = "the port associated with the server address")
parser.add_argument("-ms", "--memcachedServer",required = True, help = "the address of the memcached server")
parser.add_argument("-mp", "--memcachedPort",required = False, default = 11211, help = "the port of the memcached server")
parser.add_argument("-k", "--key",required = False, help = "the key needed to find the data in the memcached DB")
parser.add_argument("-kn", "--keyName",required = False, help = "if you're not using a configuration file, use this parameter to chose the name of the measurement")
parser.add_argument("-kr", "--keyRate", required = False, default = 5, help = "when the program is not working with a configuration file, specify the seconds between 2 different push in the influx db")
parser.add_argument("-f", "--file",required = False, help = "the configuration file path")
parser.add_argument("-fr", "--fileRate", required = False, default = 0.1, help = "when using a configuration file, specify the sleep time of the loop that check when and wich one of the key must be pushed")


args = parser.parse_args()

#log in the influx DB
#dcsMemDb
#python memcached2Influx.py -s vldantemon003.lnf.infn.it -po 8086 -f '/home/riccardo/Random bs go/Test/cofnigurationFile.txt' 
try:
    clientInflux = InfluxDBClient(host=args.influxServer, port=args.influxPort, username=args.username, password=args.password)
    clientInflux.switch_database(args.influxDatabase)
    print("succesfully logged in\n")
except:
    print("Error: impossible to connect to influx with the following parameter")
    print("username = "+args.username)
    print("password = "+args.password)
    print("database = "+args.influxServer)
    print("port = "+args.influxPort)
    sys.exit

#log in the memcached DB
#memcached_server = "192.168.198.20"
#mc_port = 11211
try:
    clientMemcached = base.Client( (args.memcachedServer , args.memcachedPort) , connect_timeout=20.0)
except:
    sys.exit('Cannot reach the memcached server, try again later')


if args.key:
    vector_key=split_list = args.key.split(",")  # Splitting at comma delimiter
    try:
        args.keyRate = int(args.keyRate)
    except ValueError as e :
        print("the inserted rate value is not valid\nThe default value of 5 second will be set")
        args.keyRate = 5
    name = ""
    if(args.keyName):
        name = args.keyName
    else:
        name = args.key
        
    while True:
        payload = []
        for s in vector_key:
            payload = jsonKey2Influx(s, clientMemcached, s)
            print('Publishing data')
            print(payload)
            clientInflux.write_points(payload)
        time.sleep(args.keyRate)

elif args.file:
    try:
        args.fileRate = float(args.fileRate)
    except ValueError as e :
        print("the inserted rate value is not valid\nThe default value of 0.1 second will be set")
        args.fileRate = 0.1
    try:
        open(args.file,'r')
    except FileNotFoundError as e:
        sys.exit("Error: " + args.iptable + " is not valid or does not point to a DBFile.")
    if os.path.isfile(args.file):
        with open(args.file,'r') as configFile:
            
            slowest = 0
            payloadList = []
            while (True):
                fileData = findTheKey(configFile)
                if fileData == None:
                    print('list done') 
                    break
                elif fileData["type"] == "json":  
                    payloadList.append(jsonData2Influx(fileData,clientMemcached))
                elif fileData["type"] == "double":
                    payloadList.append(byteData2Influx(fileData,clientMemcached))
                    
            while (True):
                time.sleep(args.fileRate)
                for payload in payloadList:
                    if (payload[0]["parameter"]["currentTime"] >= payload[0]["parameter"]["rate"]):
                        payload[0]["parameter"]["currentTime"] = 0
                        name = payload[0]["parameter"]["name"]
                        data = ({
                                "measurement": name,
                                "tags": {
                                    "key": payload[0]["parameter"]["keybind"]
                                },
                                "fields": {
                                    name : payload[0]["fields"][name]
                                    },
                        })
                        print("\nPublishing to influx:")
                        print(data)
                        print()
                        wrapData = [data]
                        clientInflux.write_points(wrapData)
                    else:
                        payload[0]["parameter"]["currentTime"] = payload[0]["parameter"]["currentTime"] +args.fileRate
                    
                
                    