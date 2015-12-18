#!/bin/bash
set -e
set -u

echo "Running base playbook..."
ansible-playbook -i hosts/localmesos-cluster --user=vagrant --ask-pass ../../ansible/base.yml
vagrant reload

echo "Running initial-cluster..."
ansible-playbook -i hosts/localmesos-cluster --user=vagrant --ask-pass --extra-vars="mesos_cluster_name=localcluster-on-`hostname` mesos_master_network_interface=ansible_eth1 mesos_slave_network_interface=ansible_eth1" ../../ansible/initial-cluster.yml

# restart Zookeeper
ansible zookeeper -i hosts/localmesos-cluster --user=vagrant -s -m service -a "name=zookeeper state=restarted" --ask-pass

# rstart mesos-master
ansible masters -i hosts/localmesos-cluster --user=vagrant -s -m service -a "name=mesos-master state=restarted" --ask-pass

# restart mesos-slave
ansible slaves -i hosts/localmesos-cluster --user=vagrant -s -m service -a "name=mesos-slave state=restarted" --ask-pass

#restart marathon
ansible marathon_servers -i hosts/localmesos-cluster --user=vagrant -s -m service -a "name=marathon state=restarted" --ask-pass
