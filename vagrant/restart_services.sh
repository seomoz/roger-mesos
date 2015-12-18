#!/bin/bash

[ ! -d "${PWD}/.vagrant" ] && echo "Move into the vagrant directory" && exit 1

i="${PWD}/.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory"

echo $i

if [[ $ROGER_MODE == 'single' ]]; then
    services=(zookeeper mesos-master mesos-slave marathon)
    for service in ${services[@]}; do
        ansible single -i $i --user vagrant -s -m service -a \
        "name=${service} state=restarted"
    done
fi
