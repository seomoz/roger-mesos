# Setting up local clusters
### Install required plugins
```
$ vagrant plugin install vagrant-triggers
$ vagrant plugin install vagrant-hostsupdater
```

The scripts here will set up a single node or a multi-node cluster with the following services installed:
```
1. Zookeeper
2. Mesos-master
3. Marathon
4. Mesos-slave
5. Docker
```
These are provided as examples with vagrant VMs. You could set up your own inventory of machines and run these scripts to get an actual cluster up and running. You can look at the definition of inventory files at
```
/vagrant/single_node/hosts/single
/vagrant/multi_node/hosts/localmesos-cluster
```

These setups also serve as a local test cluster for development purposes.

## Single-Machine cluster setup

### Setup:
1. `cd vagrant/single_node`
2. `vagrant up`
3. Verify that your local machine's `/etc/hosts` file has the entry: `192.168.2.101  localmesos01`
4. Install ansible - `sudo pip install ansible` (Note: Ansible can also be installed through the command line using brew or from the web.)
6. `./setup-single-node.sh` (both password and username is `vagrant`).
7. `http://localmesos01:5050` - ensure mesos is running.
8. `http://localmesos01:8080` - ensure marathon is running.
9. The file `/etc/mesos-master/zk` should have the following content for all the hosts:
```
zk://localmesos01:2181/mesos
```
10. The file `/etc/mesos-slave/master` should have the following content for all the hosts except localmesos01:
```
zk://localmesos01:2181/mesos
```

## Multi-node cluster setup

### Setup:
1. `cd roger/vagrant/multi_node`
2. `vagrant up`
3. Verify that your local machine's `/etc/hosts` file have the following entries:
```
   192.168.2.102  localmesos02
   192.168.2.103  localmesos03
   192.168.2.104  localmesos04
```
5. Install ansible. eg. `sudo pip install ansible` Note: Ansible can also be installed through the command line using brew or from the web.
6. `sh setup-multi-node.sh` (both username and password is `vagrant`.)
7. `http://localmesos02:5050` - ensure mesos is running.
8. `http://localmesos02:8080`- ensure marathon is running.
9. `/etc/mesos-master/zk` should have
```zk://localmesos02:2181,localmesos03:2181,localmesos04:2181/mesos```
10. `/etc/mesos-slave/master` should have
```zk://localmesos02:2181,localmesos03:2181,localmesos04:2181/mesos```

## Develepor Notes:
1. You need to know the sudo password to clear known_host entry at the time of destroying vagrant.
2. You need to be around as you need to pass on the ssh password `vagrant` mutiple times when running the the script.
3. Check your `/data/zk/logs/zookeeper.log` for any `Address already in use` exception if you find your cluster having problems in master selection (zk is not functional.)
4. Use the restart services script to restart all the services on all the hosts if required.
5. If you just restart mesos-slave it should be fine as well if resources are not getting registered.
