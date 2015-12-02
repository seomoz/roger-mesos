# Setting up local clusters
### Install required plugins
```
* vagrant plugin install vagrant-triggers
* vagrant plugin install vagrant-hostsupdater
```

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
2. `cat Vagrantfile` (Make sure only `localmesos01` is uncommented and the others `localmesos[02:04]` are commented)
3. `vagrant up`
4. Verify that your local machine's `/etc/hosts` file has the entry: `192.168.2.101  localmesos01`
5. Install ansible - `sudo pip install ansible` (Note: Ansible can also be installed through the command line using brew or from the web.)
6. `sh provision_single_cluster.sh` (both password and username is `vagrant`).
7. `http://localmesos01:5050` - ensure mesos is running.
8. `http://localmesos01:8080` - ensure marathon is running.
9. The file `/etc/mesos-master/zk` should have the following content for all the hosts:
```
zk://localmesos01:2181,localmesos02:2181,localmesos03:2181/mesos
```
10. The file `/etc/mesos-slave/master` should have the following content for all the hosts except localmesos01:
```
zk://localmesos01:2181,localmesos02:2181,localmesos03:2181/mesos
```
11. For `localmesos01` the `/etc/mesos-slave/master` file should have
```
zk://localmesos01:2181/mesos
```
The reason is that it is not configued as a slave node in `/ansible/hosts/localmesos-cluster` file.

### Good to know:
1. You need to know the sudo password as to clear known_host entry at the time of destroying vagrant.
2. You need to be around as you need to pass on the ssh password ```vagrant``` mutiple times when running the ```provision_single_cluster.sh``` script.
3. Check your /data/zk/logs/zookeeper.log for any Address already in use Exception if you find your cluster having problem in master selection=> zk is not functional
4. Use the ```./restartServicesSingleMachine.sh``` script to restart all the services if required.

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
1. `cd roger/vagrant`
2. `cat Vagrantfile` (Make sure all the machines `localmesos[01:04]` are uncommented.)
3. `vagrant up`
4. Verify that your local machine's `/etc/hosts` file have the following entries:
```
   192.168.2.101  localmesos01
   192.168.2.102  localmesos02
   192.168.2.103  localmesos03
   192.168.2.104  localmesos04
```
5. Install ansible. eg. `sudo pip install ansible` Note: Ansible can also be installed through the command line using brew or from the web.
6. `sh provision_multi_cluster.sh` (both username and password is `vagrant` If you do not see any activity taking place for the `localmesos04` node or any other node,it is probably because it's not being used in the `/ansible/hosts/localmesos-cluster` file.)
7. `http://localmesos02:5050` - ensure mesos is running.
8. `http://localmesos02:8080`- ensure marathon is running.
9. `/etc/mesos-master/zk` should have `zk://localmesos01:2181/mesos`
10. `/etc/mesos-slave/master` should have `zk://localmesos01:2181/mesos`

### Good to know:
1. You need to know the sudo password as to clear known_host entry at the time of destroying vagrant.
2. You need to be around as you need to pass on the ssh password ```vagrant``` mutiple times when running the `provision_multi_cluster.sh` script.
3. Check your `/data/zk/logs/zookeeper.log` for any Address already in use Exception if you find your cluster having problem in master selection=> zk is not functional
4. Use the `./restartServicesCluster.sh` script to restart all the services on all the hosts if required.
5. If you just restart mesos-slave it should be fine as well if resources are not getting registered.
