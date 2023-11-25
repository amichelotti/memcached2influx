import argparse
from influxdb import InfluxDBClient
from datetime import datetime
import sys  
from pymemcache.client import base
import os
import re
import json
import time
import struct

    
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

def memData2Influx(fileData,clientMemcached):
    payload = []
    memData = clientMemcached.get(fileData['keybind'])
    memcached = json.loads(memData)
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
parser.add_argument("-is", "--influxServer",required = False, help = "the address of the influx server, if not given just read memcached")
parser.add_argument("-id", "--influxDatabase", required = False, help = "the name of the database you want to log in, if not given just read memcached")
parser.add_argument("-ip", "--influxPort",required = False, default = 8086, help = "the port associated with the server address")
parser.add_argument("-ms", "--memcachedServer",required = True, help = "the address of the memcached server")
parser.add_argument("-mp", "--memcachedPort",required = False, default = 11211, help = "the port of the memcached server")
parser.add_argument("-k", "--key",required = False, help = "the key needed to find the data in the memcached DB")
parser.add_argument("-kn", "--keyName",required = False, help = "if you're not using a configuration file, use this parameter to chose the name of the measurement")
parser.add_argument("-kr", "--keyRate", required = False, default = 5, help = "when the program is not working with a configuration file, specify the seconds between 2 different push in the influx db")
parser.add_argument("-f", "--file",required = False, help = "the configuration file path")
parser.add_argument("-fr", "--fileRate", required = False, default = 1000.0, help = "when using a configuration file, specify the sleep time in milliseconds of the loop that check when and wich one of the key must be pushed")


args = parser.parse_args()

#log in the influx DB
#dcsMemDb
#python memcached2Influx.py -s vldantemon003.lnf.infn.it -po 8086 -f '/home/riccardo/Random bs go/Test/cofnigurationFile.txt' 
clientInflux=None
try:
    if args.influxServer:
        clientInflux = InfluxDBClient(host=args.influxServer, port=args.influxPort, username=args.username, password=args.password)
        clientInflux.switch_database(args.influxDatabase)
        print(f"Succesfully logged in {args.influxServer} db {args.influxDatabase}")
    else:
        print("NO INFLUX SPECIFIED, PERFORM MEMCACHED READ ONLY")
        
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
            if clientInflux:
                clientInflux.write_points(payload)
        time.sleep(args.keyRate)

elif args.file:
    try:
        args.fileRate = float(args.fileRate)
    except ValueError as e :
        print("the inserted rate value is not valid\nThe default value of 0.1 second will be set")
        args.fileRate = 0.1
    with open(args.file,'r') as jsonfile:
        tofetch=json.load(jsonfile)['dataset']
        cache={}
        for k in tofetch:
            k['time']=time.time()
            if not 'rate' in k:
                k['rate']=5
        vdatapoints=[]
        while (True):
            now=time.time()
            for k in tofetch:
                if (now-k['time']) > k['rate']:
                    if k['keybind'] in cache and now-cache[k['keybind']]['time']<k['rate']:
                        ## take data from cache
                        memData = cache[k['keybind']]['data']
                        k['time']=cache[k['keybind']]['time']

                    else:
                        memData = clientMemcached.get(k['keybind'])
                        cache[k['keybind']]={'data':memData,'time':now}
                        k['time']=now
                    if k['type'] == "json":
                        jvalue=memData.decode('utf-8')
                        dictj=json.loads(jvalue)
                        if len(dictj.keys())==1:
                            ## the dict is named
                            val=next(iter(dictj.values()))
                            if isinstance(val,dict):
                                dictj=val
                            
                        for item in dictj.items():
                            key, value = item
                            if isinstance(value, (int, float, str, bool)):
                                no_spaces = key.replace(" ", "")

                                pattern = re.compile('[\W_]+')
                                result = re.sub(pattern, '', no_spaces)
                                # print(f'Key: {result.lower()}, Value: {value}')
                                if isinstance(value,(int,float)):
                                    if 'factor' in k:
                                        value=value*k['factor']
                                    if 'offset_value' in k:
                                        value=value+k['offset_value']
                                        
                                data_point = {
                                    "measurement": k['name'],
                                    "time": datetime.utcnow(),
                                    "fields": {result.lower():value}
                                }
                                vdatapoints.append(data_point)

                    else:
                        if k['offset']<0:
                            ## start from end
                            k['offset']=len(memData)+k['offset']
                        byteArray=memData[k['offset']:k['offset']+k['len']]
                        fields = {} 
                        offset_value=0
                        factor_value=1
                        bigendian=""
                        value = None
                        if 'lbe' in k  and not k['lbe']: ## big endian
                            bigendian=">"
                            
                        if 'factor' in k:
                            factor_value=k['factor']
                        if 'offset_value' in k:
                            offset_value=k['offset_value']

                        if k['type'] == "double":
                            value = struct.unpack(bigendian+'d', byteArray)[0]
                            value = value*factor_value + offset_value
                        if k['type'] == "int" or k['type'] == "int32":
                                value = struct.unpack(bigendian+'i', byteArray)[0]
                                value = value*factor_value + offset_value

                        if k['type'] == "int64" :
                                value = struct.unpack(bigendian+'q', byteArray)[0]
                                value = value*factor_value + offset_value
                        if k['type'] == "bool" :
                                value =bool(byteArray[0])
                        if k['type'] == "string" :
                                value =byteArray.decode('utf8')
                        if k['type'] == "vdouble":
                                nvals=k['len']//8
                                value = struct.unpack(bigendian+'d'*nvals, byteArray)
                                result_vector = [(val * factor_value + offset_value) for val in value]
                                value=result_vector
                                    
                        if value is not None:
                            fname='val'
                            if 'varname' in k:
                                fname=k['varname']
            
                            if isinstance(value,list):
                                cnt=0
                                for v in value:
                                    if isinstance(fname,list): 
                                        fields = {fname[cnt]: v}
                                    else:
                                        fields = {fname+str(cnt): v}
                                    data_point = {
                                    "measurement": k['name'],
                                    "time": datetime.utcnow(),
                                    "fields": fields
                                    }
                                    vdatapoints.append(data_point)
                                    cnt=cnt+1
                                    
                            else:
                                fields = {fname: value}
                                data_point = {
                                "measurement": k['name'],
                                "time": datetime.utcnow(),
                                "fields": fields
                                }
                                vdatapoints.append(data_point)

            if len(vdatapoints):
                print(vdatapoints)

                if clientInflux:
                    clientInflux.write_points(vdatapoints)
                vdatapoints=[]

            time.sleep(args.fileRate/1000.0)