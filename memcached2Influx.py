import argparse
from influxdb import InfluxDBClient
import sys
from pymemcache.client import base
import os
import re


def findTheKey(path, clientMemcached):
    with open(path,'r') as configFile:
        data = {}
        pattern = r'^"(.+)":(.+,(( ←)|[^a-zA-Z ]))'
        for line in configFile:
            match = re.search(pattern,line)
            if(match):
                match = re.search(pattern,line)
                parameter = re.sub(r',|"|( ←)',"",match.group(2))
                data[match.group(1)] = parameter
            if(line.find('keybind') != -1):
                match = re.search(pattern,line)
                parameter = re.sub(r',|"|( ←)',"",match.group(2))
                data[match.group(1)] = parameter
                #value

            

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
#dcsMemDb
try:
    clientInflux = InfluxDBClient(host=args.server, port=args.port, username=args.username, password=args.password)
    print("succesfully logged in")
except:
    sys.exit("Error: Invalid parameters, please try again")

#log in the memcached DB
#memcached_server = "192.168.198.20"
#mc_port = 11211
try:
    clientMemcached = base.Client( ("192.168.198.20" , 11211) , connect_timeout=20.0)
except:
    sys.exit('Cannot reach the memcached server, try again later')
    
#try:
  #  if os.path.isfile(args.file):
key = findTheKey(args.file, clientMemcached)
#except FileNotFoundError as e:
 #   sys.exit("Error: " + args.iptable + " is not valid or does not point to a DBFile.")