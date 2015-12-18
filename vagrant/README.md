## Single-Machine cluster setup
This will set up a single machine with the following services installed:
```
1. Zookeeper
2. Mesos-master
3. Marathon
4. Mesos-slave
5. Docker
```

You can look at the definition of this file at
```
/ansible/hosts/single
```

### Setup:
1. `cd vagrant`
2. `vagrant up`
3. `curl http://localmesos01:5050` - ensure mesos is running.
4. `curl http://localmesos01:8080` - ensure marathon is running.
5. The file `/etc/mesos-master/zk` should have the following content for all the hosts:
```
zk://localmesos01:2181,localmesos02:2181,localmesos03:2181/mesos
```
6. The file `/etc/mesos-slave/master` should have the following content for all the hosts except localmesos01:
```
zk://localmesos01:2181,localmesos02:2181,localmesos03:2181/mesos
```
7. For `localmesos01` the `/etc/mesos-slave/master` file should have
```
zk://localmesos01:2181/mesos
```
The reason is that it is not configued as a slave node in `/ansible/hosts/localmesos-cluster` file.

### Good to know:
1. You need to know the sudo password as to clear known_host entry at the time of destroying vagrant.
2. Check your /data/zk/logs/zookeeper.log for any Address already in use Exception if you find your cluster having problem in master selection=> zk is not functional
3. Use the ```./restart_services.sh``` script to restart all the services if required.

## Multiple-Machine cluster setup (3 by default)
This will set up a single machine with the following services installed
1. Mesos-master
2. Mesos-slave
3. Zookeeper
4. Marathon
5. Docker

You can look at the definition of this file at
```
/roger/ansible/hosts/localmesos-cluster
```

### Setup:
1. `cd vagrant`
2. `vagrant up`
3. `curl http://localmesos02:5050` - ensure mesos is running.
4. `curl http://localmesos02:8080`- ensure marathon is running.
5. `/etc/mesos-master/zk` should have `zk://localmesos01:2181/mesos`
6. `/etc/mesos-slave/master` should have `zk://localmesos01:2181/mesos`

### Good to know:
1. You need to know the sudo password as to clear known_host entry at the time of destroying vagrant.
2. Check your `/data/zk/logs/zookeeper.log` for any Address already in use Exception if you find your cluster having problem in master selection=> zk is not functional
3. Use the `./restart_services.sh` script to restart all the services on all the hosts if required.
4. If you just restart mesos-slave it should be fine as well if resources are not getting registered.
