# roger-mesos

This repo contains everything you need to set up a complete Mesos cluster with the following components -

* [zookeeper](https://zookeeper.apache.org/)
* [mesos](http://mesos.apache.org/) (masters + slaves)
* [marathon](https://mesosphere.github.io/marathon/)
* [chronos](http://mesos.github.io/chronos/)
* [docker](https://www.docker.com/) (on the slaves)
* [haproxy](http://www.haproxy.org/) + [roger-bamboo](https://github.com/seomoz/roger-bamboo) (for load-balancing/proxy)

It also contains examples that use Vagrant VMs to illustrate how to set up a cluster (see [vagrant/](vagrant)).

### Pre-requisites
* [Ansible](http://docs.ansible.com/ansible/intro.html) is installed on the control machine (prior knowledge of [ansible](http://docs.ansible.com/ansible/index.html) helps.)
* Inventory (aka a set of host machines) exists and have ubuntu 14.0.4 LTS along with openssh-server installed.
* Sudo access to each of the host machines is available.

If you are only looking for a vagrant based cluster running on your machine for development/testing purposes go to the [vagrant/](vagrant) directory.

### Steps to get (a real) cluster up and running
* Ensure that an inventory file exists with the list of masters, slaves, etc. (see an existing hosts file in the hosts dir under [vagrant/single_node or vagrant/multi_node](vagrant)).
* Run the following commands (*_WARNING:_* the first command below will reboot the hosts):
```
$ ansible-playbook -i <path-to-hosts-file> --user=<user> --ask-pass --ask-sudo-pass --extra-vars="restart_machine=true" base.yml
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

### Notes
* The `--ask-pass` and `--ask-sudo-pass` are not needed if ssh key is added and the user is part of the sudo group in the host machines.
* To restart a service on all hosts, you can use ansible's service module. For example:
```
$ ansible zookeeper -i <path/to/hosts/file> --user=<user> --ask-pass --ask-sudo-pass -m service -a "name=zookeeper state=restarted" -s
$ ansible marathon_servers -i <path/to/hosts/file> --user=<user> --ask-pass --ask-sudo-pass -m service -a "name=marathon state=restarted" -s
```
* For marathon generate permissions the various variables are required to be available. Using ansible vault is one way to do this. Example -
```
$ ansible-playbook -i /path/to/inventory/file ansible/marathon-nodes.yml -e @$HOME/my-ansible-secrets.yml.encrypted --vault-password-file ~/.my-ansible-secrets-vault-pass
