#!/bin/bash
OPTIND=1

HOSTS_FILE=""
MARATHON_VERSION=""
MASTER_HOST=""

while getopts ":i:m:v:h" opt; do
  case $opt in
    h)
      echo "Usage: upgrade-marathon.sh -i <ansible hosts file> -m <main marathon host> -v <marathon version>" >&2
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
      MARATHON_VERSION=$OPTARG
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

if [[ -z "${MARATHON_VERSION}" ]]; then
  echo 'A value for -v is required.'
  exit 1
fi


echo "About to upgrade marathon to version $MARATHON_VERSION using masters from $HOSTS_FILE with $MASTER_HOST as the main host." &&\
echo "Press enter to continue." &&\
read &&\
echo "Updating apt" &&\
ansible -i "$HOSTS_FILE" masters --become -m shell -a "apt-get update" &&\
echo "Upgrading marathon." &&\
ansible -i "$HOSTS_FILE" masters --become -m shell -a "apt-get install marathon\=${MARATHON_VERSION}" &&\
echo "Stopping marathon." &&\
ansible -i "$HOSTS_FILE" masters --become -m shell -a "service marathon stop" --limit='!'${MASTER_HOST} &&\
echo "Restarting marathon on main host." &&\
ansible -i "$HOSTS_FILE" masters --become -m shell -a "service marathon restart" --limit=${MASTER_HOST} &&\
echo "Verify that Marathon came up on $MASTER_HOST and then press enter to continue." &&\
read &&\
ansible -i "$HOSTS_FILE" masters --become -m shell -a "service marathon start" --limit='!'${MASTER_HOST} &&\
echo "Done."

