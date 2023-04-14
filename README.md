# memcached2Influx

### prerequisite installation

`pip install -r requirements.txt`

### help
usage: memcached2Influx.py [-h] [-u USERNAME] [-p PASSWORD] [-s SERVER] [-d DATABASE]
                           [-f FILE] [-n NAME] [-k KEY] [-po PORT] [-r RATE]

options:
  `-h` or `--help`	show this help message and exit
  `-u` or `--username` --username USERNAME
                        the username needed to log in the db
  `-p` or `--password` --password PASSWORD
                        the password needed to log in the db
  `-s` or `--server` --server SERVER
                        the ip address of the server
  `-d` or `--database` --database DATABASE
                        the name of the database you want to log in
  `-f` or `--file` --file FILE  the configuration file path
  `-n` or `--name` --name NAME  if you're not using a configuration file, use this parameter to
                        chose the name of the measurement
  `-k` or `--key` KEY     the key needed to find the data in the memcached DB
  `-po` or `--port` PORT	the port associated with the server address
  `-r` or `--rate` RATE  specify the seconds between 2 different push in the influx db,
                        use this option only if you're not using a configuration file

### test
some test of funtionality
```
python memcached2Influx.py -s vldantemon003.lnf.infn.it -po 8086 -f '/home/riccardo/Random bs go/Git/memcached2influx/memcached2influx/cofnigurationFile.txt' 
or
ython memcached2Influx.py -s vldantemon003.lnf.infn.it -po 8086 -k DAFNESTATELAB_JDAT -r 10
```
