#!/bin/bash
OPTIND=1

HOSTS_FILE=""
MESOS_VERSION=""
MASTER_HOST=""

while getopts ":i:m:v:h" opt; do
  case $opt in
    h)
      echo "Usage: upgrade-mesos.sh -i <ansible hosts file> -m <main mesos host> -v <mesos version>" >&2
      exit 0;
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
    m)
      MASTER_HOST=$OPTARG
      ;;
    i)
      HOSTS_FILE=$OPTARG
      ;;
    v)
      MESOS_VERSION=$OPTARG
      ;;
  esac
done

if [[ -z "${MASTER_HOST}" ]]; then
  echo 'A value for -m is required.'
  exit 1
fi

if [[ -z "${HOSTS_FILE}" ]]; then
  echo 'A value for -i is required.'
  exit 1
fi

if ! [[ -e "${HOSTS_FILE}" ]]; then
  echo "${HOSTS_FILE} does not exist."
  exit 1
fi

if [[ -z "${MESOS_VERSION}" ]]; then
  echo 'A value for -v is required.'
  exit 1
fi


echo "About to upgrade mesos to version $MESOS_VERSION using masters from $HOSTS_FILE with $MASTER_HOST as the main host." &&\
echo "Press enter to continue." &&\
read &&\
echo "Updating apt on masters and slaves." &&\
ansible -i "$HOSTS_FILE" masters --become -m shell -a "apt-get update" &&\
ansible -i "$HOSTS_FILE" slaves  --become -m shell -a "apt-get update" &&\
echo "Upgrading mesos package on masters." &&\
ansible -i "$HOSTS_FILE" masters --become -m shell -a "apt-get install mesos\=${MESOS_VERSION}" &&\
echo "Upgrading mesos package on slaves." &&\
ansible -i "$HOSTS_FILE" slaves  --become -m shell -a "apt-get install mesos\=${MESOS_VERSION}" &&\
echo "Restarting mesos-master on ${MASTER_HOST}" &&\
ansible -i "$HOSTS_FILE" masters --become -m shell -a "service mesos-master restart" --limit=${MASTER_HOST} &&\
echo "Check the mesos UI on ${MASTER_HOST} to see if it is working.  Press enter to continue." &&\
read &&\
echo "Restarting mesos-master on remaining masters one by one." &&\
ansible -i "$HOSTS_FILE" masters --become -m shell -a "service mesos-master restart" --forks=1 --limit='!'${MASTER_HOST} &&\
echo "Restarting mesos-slave on all slaves." &&\
ansible -i "$HOSTS_FILE" slaves  --become -m shell -a "service mesos-slave restart" &&\
echo "Done."

