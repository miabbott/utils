#!/usr/bin/env python

import argparse
import os
import re
import subprocess
import sys

IMAGES_DIR = '/var/lib/libvirt/images/'

parser = argparse.ArgumentParser(description="Create QCOW2 images and spin " +
                                             "up VMs with them")
parser.add_argument('image', metavar='image', type=str,
                    help='the name of an image in %s' % IMAGES_DIR)
parser.add_argument('-c', '--clean', action='store_true',
                    help='only clean up existing instances')
parser.add_argument('-i','--images-dir', action='store',
                    help='[NOT IMPLEMENTED] alternate location for images')
parser.add_argument('-m', '--meta-data', type=str, action='store',
                    help='[NOT IMPLEMENTED] path to meta-data file for cloud-init')
parser.add_argument('-n', '--num-instances', type=int, action='store',
                    help='number of image instances and VMs to create')
parser.add_argument('-u', '--user-data', type=str, action='store',
                    help='[NOT IMPLEMENTED] path to user-data file for cloud-init')
args = parser.parse_args()


file_list = os.listdir(IMAGES_DIR)

image_name_re = re.compile("(.+)(\.qcow2|\.iso)")
m = image_name_re.search(args.image)
if m:
    image_name = m.group(1)
    image_type = m.group(2)
else:
    sys.exit("ERROR: Image name does not look recognizable")

if args.clean:
    for f in file_list:
        if image_name + "-instance" in f:
            os.remove(IMAGES_DIR + f)
            print "Removed: %s" % f
    sys.exit()

if args.num_instances:
    num_instances = args.num_instances
else:
    num_instances = 1

fp_to_image = IMAGES_DIR + args.image
assert os.path.isfile(fp_to_image)
print "Found image at: %s" % fp_to_image

for n in range(num_instances):
    instance_name = image_name + '-instance-' + str(n)
    instance_file = instance_name + image_type
    fp_to_instance = IMAGES_DIR + instance_file
    if instance_file in file_list:
        print "Found existing image instance %s; it will now be removed" % instance_file
        os.remove(fp_to_instance)

    print "Creating new image instance: %s" % fp_to_instance
    subprocess.check_call(['qemu-img',
                           'create',
                           '-f', 'qcow2',
                           '-o', 'backing_file=%s' % fp_to_image,
                           fp_to_instance])

    # print "Starting VM using new instance"
    # subprocess.check_call(['virt-install',
    #                        '--import',
    #                        '--name', instance_name,
    #                        '--ram', '2048',
    #                        '--disk', 'path=%s,format=qcow2,bus=virtio' % fp_to_instance,
    #                        '--disk', 'path=%s,device=cdrom' % fp_to_ci_iso,
    #                        '--network', 'bridge=virbr0',
    #                        '--os-type', 'linux',
    #                        '--os-variant', 'rhel7'])

# virt-install --import --name rhel-atomic-cloud-7.1-3-instance-0 --ram 2048 --disk path=/var/lib/libvirt/images/rhel-atomic-cloud-7.1-3.x86_64-instance-0.qcow2,format=qcow2,bus=virtio --disk path=/var/lib/libvirt/images/rhel-atomic-cloud-7.1-3-0-cidata.iso,device=cdrom --network bridge=virbr0 --graphics vnc --os-type linux --os-variant rhel7

# genisoimage -output /var/lib/libvirt/images/rhel-atomic-cloud-7.1-3-0-cidata.iso -volid cidata -joliet -rock user-data meta-data