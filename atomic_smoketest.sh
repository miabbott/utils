#!/bin/bash

DATA_DIR=/var/qe
DATA_FILE=atomic_smoke_output.txt
FULL_PATH=$DATA_DIR/$DATA_FILE
KEY_PKGS="docker docker-python docker-storage-setup etcd flannel kernel kubernetes subscription-manager"
BIOS_VERSION=UNKNOWN
GRUBFILE=UNKNOWN

# Determine if system is EFI or not
if [ -f /boot/grub2/grub.cfg ];then
  BIOS_VERSION=grub
  GRUBFILE=/boot/grub2/grub.cfg
elif [ -f /boot/efi/EFI/redhat/grub.cfg ];then
  BIOS_VERSION=EFI
  GRUBFILE=/boot/efi/EFI/redhat/grub.cfg
fi

# Create DATA_DIR; adjust SELinux context
if [ ! -d "$DATA_DIR" ]; then
    mkdir -p $DATA_DIR
    chcon -Rt svirt_sandbox_file_t $DATA_DIR
fi

# Remove any existing smoketest files
if [ -e "$FULL_PATH" ]; then
    rm $FULL_PATH
fi

# Send all STDOUT to file
exec 1>> $FULL_PATH

# Test Atomic host installation, so there should only be one match
echo -n "Testing version: "
grep Atomic $GRUBFILE | awk 'BEGIN {FS="'"'"'"}{print $2}'
echo -en "\nTest Platform: "
virt-what
echo "\nBIOS Version: $BIOS_VERSION\n"

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
