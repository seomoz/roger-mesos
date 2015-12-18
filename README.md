# roger-mesos

This repo contains everything you need to set up a complete Mesos cluster with the following components -

* [zookeeper](https://zookeeper.apache.org/)
* [mesos](http://mesos.apache.org/) (masters + slaves)
* [marathon](https://mesosphere.github.io/marathon/)
* [chronos](http://mesos.github.io/chronos/)
* [docker](https://www.docker.com/) (on the slaves)
* [haproxy](http://www.haproxy.org/) + [roger-bamboo](https://github.com/seomoz/roger-bamboo) (for load-balancing/proxy)

It also contains examples to show how to set up single as well as multi-node clusters using Vagrant VMs (see [vagrant/](vagrant)).

### Pre-requisites
* [Ansible](http://docs.ansible.com/ansible/intro.html) is installed on the control machine (prior knowledge of [ansible](http://docs.ansible.com/ansible/index.html) helps.)
* Inventory (aka a set of host machines) exists and have ubuntu 14.0.4 LTS along with openssh-server installed.
* Sudo access to each of the host machines is available.

### Steps to get the cluster up and running
* Ensure that an inventory file exists with the list of masters, slaves, etc. (see an existing hosts file in the hosts dir under [vagrant](vagrant).)
* Run the following commands (*WARNING:* the first command below will reboot the hosts):
```
cd vagrant
vagrant up
```

### To set up and start docker registry
* Make sure host file contains docker_registry group.
* Run:
```
cd vagrant
ansible-playbook -i $PWD/.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory --user=vagrant docker-registry.yml
```

Restarting services

```
./restart_services.sh
```

### Single vs Multiple Instaces
This configuration sets up a single node environment by default. This is
controlled by the environment variable ROGER_MODE. Set to multi to setup a
three node cluster.
