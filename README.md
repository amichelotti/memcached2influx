# memcached2Influx

### prerequisite installation

`pip install -r requirements.txt`

### help
usage: memcached2Influx.py [-h] [-u USERNAME] [-p PASSWORD] -is INFLUXSERVER
                           -id INFLUXDATABASE [-ip INFLUXPORT] -ms
                           MEMCACHEDSERVER [-mp MEMCACHEDPORT] [-k KEY]
                           [-kn KEYNAME] [-kr KEYRATE] [-f FILE]
                           [-fr FILERATE]


options:
  `-h` or `--help`            show this help message and exit

  `-u` or `--username`    the username needed to log in the db
  
  `-p` or `--password`    the password needed to log in the db

  `-is` or `--influxServer`   the address of the influx server

  `-id` or `--influxDatabase`   the name of the database you want to log in

  `-ip` or `--influxPort`    the port associated with the server address

  `-ms` or `--memcachedServer`    the address of the memcached server

  `-mp` or `--memcachedPort`    the port of the memcached server

  `-k` or `--key`   the key needed to find the data in the memcached DB

  `-kn` or `--keyName`    if you're not using a configuration file, use this parameter to chose the name of the measurement

  `-kr` or `--keyRate`    when the program is not working with a configuration file, specify the seconds between 2 different push in the influx db

  `-f` or `--file`    the configuration file path

  `-fr` or `--fileRate`   when using a configuration file, specify the sleep time of the loop that check when and wich one of the key must be pushed


### test
some test of funtionality
```
python memcached2Influx.py -is vldantemon003.lnf.infn.it -id dcsMemDb -ip 8086 -ms 192.168.198.20 -mp 11211 -f '/home/riccardo/Random bs go/Git/memcached2influx/memcached2influx/configurationFile.txt' 

or
python memcached2Influx.py -is vldantemon003.lnf.infn.it -ip 8086 -id dcsMemDb 
-k DAFNESTATELAB_JDAT -kn test -kr 10 -ms 192.168.198.20 -mp 11211
```
### usage
this application has benn made to transfer data from a memcached server to an influx server, but there are 2 different way to do so.

`using a configuration file.`
In the project folder you can find a "configurationFile.txt" this file contain all the necessary data to retrive and optimize the process of transiction between the 2 server, and in order to use such file you should use a command line like this:
```
python memcached2Influx.py -is vldantemon003.lnf.infn.it -id dcsMemDb -ip 8086 -ms 192.168.198.20 -mp 11211 -f '/home/riccardo/Random bs go/Git/memcached2influx/memcached2influx/configurationFile.txt' 

```
`using key and rate`
But if you don't have all this information all you don't want to use a configuration file, you can just use a key and a rate instead.
With just a key and a publishing rate the program will know just what data you want to pubish and at wich rate, in order to do so you should use a command line like this
```
python memcached2Influx.py -is vldantemon003.lnf.infn.it -ip 8086 -id dcsMemDb 
-k DAFNESTATELAB_JDAT -kn test -kr 10 -ms 192.168.198.20 -mp 11211
```