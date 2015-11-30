# roger-mesos

This repo contains a set of ansible playbooks to set up a complete Mesos cluster with the following components -

* [zookeeper](https://zookeeper.apache.org/)
* [mesos](http://mesos.apache.org/) (masters + slaves)
* [marathon](https://mesosphere.github.io/marathon/)
* [chronos](http://mesos.github.io/chronos/)
* [docker](https://www.docker.com/) (on the slaves)
* [haproxy](http://www.haproxy.org/) + [roger-bamboo](https://github.com/seomoz/roger-bamboo) (for load-balancing/proxy)

It also contains examples to show how to set up single as well as multi-node clusters using Vagrant VMs (see [vagrant](vagrant)).

### Pre-requisites
* Ansible is installed on the control machine (prior knowledge of ansible helps.)
* Inventory (aka host machines) exist and have ubuntu 14.0.4 LTS along with openssh-server installed.
* Sudo access to the host machines is available.

### Steps to get the cluster up and running
* Ensure that an inventory file exists with the list of masters, slaves, etc. (see an existing hosts file in the hosts dir under [vagrant](vagrant).)
* Run:
```
$ ansible-playbook -i <path-to-hosts-file> --user=<user> --ask-pass --ask-sudo-pass zookeeper-nodes.yml
$ ansible-playbook -i <path-to-hosts-file> --user=<user> --ask-pass --ask-sudo-pass --extra-vars="mesos_cluster_name=<cluster-name-to-use>" master-nodes.yml
$ ansible-playbook -i <path-to-hosts-file> --user=<user> --ask-pass --ask-sudo-pass marathon-nodes.yml
$ ansible-playbook -i <path-to-hosts-file> --user=<user> --ask-pass --ask-sudo-pass chronos.yml
$ ansible-playbook -i <path-to-hosts-file> --user=<user> --ask-pass --ask-sudo-pass slave-nodes.yml
$ ansible-playbook -i <path-to-hosts-file> --user=<user> --ask-pass --ask-sudo-pass bamboo-nodes.yml
```

### To set up and start docker registry
* Make sure host file contains docker_registry group.
* Run:
```
$ ansible-playbook -i <path-to-hosts-file> --user=<user> --ask-pass --ask-sudo-pass docker-registry.yml
```
