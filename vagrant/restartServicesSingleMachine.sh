# !/bin/bash

# restart Zookeeper
ansible zookeeper -i ../ansible/hosts/single --user=vagrant -s -m service -a "name=zookeeper state=restarted" --ask-pass

# rstart mesos-master
ansible masters -i ../ansible/hosts/single --user=vagrant -s -m service -a "name=mesos-master state=restarted" --ask-pass

# restart mesos-slave
ansible slaves -i ../ansible/hosts/single --user=vagrant -s -m service -a "name=mesos-slave state=restarted" --ask-pass

#restart marathon
ansible marathon_servers -i ../ansible/hosts/single --user=vagrant -s -m service -a "name=marathon state=restarted" --ask-pass
