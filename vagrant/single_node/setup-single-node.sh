#!/bin/bash
set -e
set -u

echo "Kernel reload()..."
ansible-playbook -i hosts/single --user=vagrant --ask-pass ../../ansible/base.yml
vagrant reload

echo "Starting ansible-playbook to set up other services..."

ansible-playbook -i hosts/single --user=vagrant --ask-pass --extra-vars="mesos_cluster_name=localcluster-on-`hostname` mesos_master_network_interface=ansible_eth1 mesos_slave_network_interface=ansible_eth1" ../../ansible/initial-cluster.yml --diff -e "@../../ansible_vars.yml"

# restart Zookeeper
ansible zookeeper -i hosts/single --user=vagrant -s -m command -a "service zookeeper restart" --ask-pass

# rstart mesos-master
ansible masters -i hosts/single --user=vagrant -s -m command -a "service mesos-master restart" --ask-pass

# restart mesos-slave
ansible slaves -i hosts/single --user=vagrant -s -m command -a "service mesos-slave restart" --ask-pass

#restart marathon
ansible marathon_servers -i hosts/single --user=vagrant -s -m command -a "service marathon restart" --ask-pass
