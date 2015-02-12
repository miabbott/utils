#!/bin/bash

DATA_DIR=/var/qe
DATA_FILE=atomic_smoke_output.txt
FULL_PATH=$DATA_DIR/$DATA_FILE
KEY_PKGS="docker etcd flannel kernel kubernetes subscription-manager"

mkdir -p $DATA_DIR
chcon -Rt svirt_sandbox_file_t $DATA_DIR

echo -e "Atomic Host Status:\n" > $FULL_PATH

atomic host status >> $FULL_PATH

echo -e "\nKey Packages:\n" >> $FULL_PATH

rpm -q $KEY_PKGS >> $FULL_PATH

rpm -qa | grep atomic | sort >> $FULL_PATH

rpm_count=$(rpm -qa | wc -l)

echo -e "\nTotal RPM Count: $rpm_count\n" >> $FULL_PATH

echo -e "Full RPM List: \n" >> $FULL_PATH

rpm -qa | sort >> $FULL_PATH

