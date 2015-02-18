#!/bin/bash

DATA_DIR=/var/qe
DATA_FILE=atomic_smoke_output.txt
FULL_PATH=$DATA_DIR/$DATA_FILE
KEY_PKGS="docker docker-python docker-storage-setup etcd flannel kernel kubernetes subscription-manager"

if [ ! -d "$DATA_DIR" ]; then
    mkdir -p $DATA_DIR
    chcon -Rt svirt_sandbox_file_t $DATA_DIR
fi

if [ -e "$FULL_PATH" ]; then
    rm $FULL_PATH
fi

exec 1>> $FULL_PATH

echo "cat /etc/redhat-release"
cat /etc/redhat-release

echo -e "\nAtomic Host Status:\n"
atomic host status

echo -e "\nKey Packages:\n"
rpm -q $KEY_PKGS
rpm -qa | grep atomic | sort

rpm_count=$(rpm -qa | wc -l)

echo -e "\nTotal RPM Count: $rpm_count\n"

echo -e "Full RPM List: \n"
rpm -qa | sort
