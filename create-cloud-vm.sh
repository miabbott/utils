#!/bin/sh
# Originally by Colin Walters <walters@verbum.org>
#
# Clone a copy-on-write "gold" cloud image, resize it to the target, and
# use virt-install to create a VM, attaching a cloud-init metadata ISO.
# Run in /var/lib/libvirt/images

img=$1
shift
name=$1
shift
size=$1
shift

set -e
set -x

disk=$(pwd)/$name.qcow2

qemu-img create -f qcow2 -o "backing_file=$img" "$disk" $size
exec virt-install --force --noautoconsole --name "$name" --ram 1024 --import --disk=${disk} --disk=$(pwd)/gold/insecure-vagrant-userdata.iso,device=cdrom --os-variant rhel7 "$@"
