#!/bin/bash

DATA_DIR=/var/qe
DATA_FILE=atomic_smoke_output.txt
FULL_PATH=$DATA_DIR/$DATA_FILE
KEY_PKGS="docker docker-python docker-storage-setup etcd flannel kernel kubernetes subscription-manager"
BIOS_VERSION=UNKNOWN
GRUBFILE=UNKNOWN
KEY_ID="199e2f91fd431d51"
SMOKE_STATUS="0"

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

# Test the boot entry for mention of Atomic
grep -q Atomic $GRUBFILE
if [ $? -ne 0 ]
then
    SMOKE_STATUS="1"
    echo -e "\nERROR! $GRUBFILE does not have any mention of RHEL Atomic Host"
else
    echo -n "Testing version: "
    grep -m 1 Atomic $GRUBFILE | awk 'BEGIN {FS="'"'"'"}{print $2}'
fi

echo -en "\nTest Platform: "
virt-what
echo -e "\nBIOS Version: $BIOS_VERSION\n"

grep -q "Red Hat Enterprise Linux Atomic Host" /etc/redhat-release
if [ $? -ne 0 ]
then
    SMOKE_STATUS="1"
    echo -e "\nERROR in /etc/redhat-release\n"
fi
echo "# cat /etc/redhat-release"
cat /etc/redhat-release

echo -e "\nAtomic Host Status:\n"
atomic host status

echo -e "\nVerify Signature on Installed Packages:\n"
failed_pkgs=""
for pkg in `rpm -qa`
do
    pkg_info=`rpm -qi $pkg`
    if [[ $pkg_info != *$KEY_ID* ]]
    then
        SMOKE_STATUS="1"
        failed_pkgs="$failed_pkgs\n$pkg"
    fi
done
if [ -n "$failed_pkgs" ]
then
    echo -e "FAILED!\n"
    echo -e "Packages with Invalid Signatures:\n"
    echo -e "$failed_pkgs" | sort
else
    echo -e "PASSED!"
fi

echo -e "\nKey Packages:\n"
rpm -q $KEY_PKGS
rpm -qa | grep atomic | sort

rpm_count=$(rpm -qa | wc -l)

echo -e "\nTotal RPM Count: $rpm_count\n"

echo -e "Full RPM List: \n"
rpm -qa | sort

if [ "$SMOKE_STATUS" == "1" ]
then
    touch $DATA_DIR/atomic_smoke_failed
fi