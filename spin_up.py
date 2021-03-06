#!/usr/bin/env python

'''
TODO: support ISO installs
TODO: auto-generate user-data (copy in id_rsa.pub, etc)
TODO: remove existing guests via 'virsh undefine'
TODO: fix clean option to only require image name
TODO: cloud-init ISO must use strict filenames 'meta-data' and 'user-data'
'''

import argparse
import os
import re
import subprocess
import sys
import time


def generate_ci_iso(name=None, user_data=None, meta_data=None, image_dir=None):
    if name is None or user_data is None:
        print ("ERROR: need to provide an instance name and the path to" +
               "user-data file")
        return 1

    if not os.path.isfile(user_data):
        print ("ERROR: could not find user-data file at specified " +
               "location: %s" % user_data)

    iso_name = name + "-cidata.iso"
    if image_dir is None:
        fp_to_iso = "/var/lib/libvirt/images/" + iso_name
    else:
        fp_to_iso = image_dir + iso_name

    if meta_data is None:
        md_f = open('/tmp/meta-data', 'w')
        md_f.write("instance-id: %s\n" % name)
        md_f.write("local-hostname: %s\n" % name)
        md_f.close()
        meta_data = '/tmp/meta-data'

    cmd = ["/usr/bin/genisoimage", "-output", fp_to_iso, "-volid", "cidata",
           "-joliet", "-rock", user_data, meta_data]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print "ERROR: unable to generate cidata ISO"
        print err
        return 1

    return fp_to_iso

IMAGES_DIR = '/var/lib/libvirt/images/'

parser = argparse.ArgumentParser(description="Create QCOW2 images and spin " +
                                             "up VMs with them")
parser.add_argument('image', type=str,
                    help='the name of an image in %s' % IMAGES_DIR)
parser.add_argument('user_data', type=str,
                    help='path to user-data file for cloud-init')
parser.add_argument('-c', '--clean', action='store_true',
                    help='only clean up existing instances')
parser.add_argument('-i', '--images-dir', action='store',
                    help='[NOT IMPLEMENTED] alternate location for images')
parser.add_argument('-m', '--meta-data', type=str, action='store',
                    help='[NOT IMPLEMENTED] path to meta-data file for ' +
                         'cloud-init')
parser.add_argument('-n', '--num-instances', type=int, action='store',
                    help='number of image instances and VMs to create')
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
        print "Removing existing instance %s; " % instance_file
        os.remove(fp_to_instance)

    print "Creating new image instance: %s" % fp_to_instance
    qemu_cmd = ['/usr/bin/qemu-img', 'create', '-f', 'qcow2', '-o',
                'backing_file=%s' % fp_to_image, fp_to_instance]
    qemu_p = subprocess.Popen(qemu_cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    qemu_out, qemu_err = qemu_p.communicate()
    if qemu_p.returncode != 0:
        print qemu_err
        continue

    print "Creating new cloud-init ISO"
    fp_to_ci_iso = generate_ci_iso(name=instance_name,
                                   user_data=args.user_data)
    if fp_to_ci_iso == 1:
        print "ERROR: unable to generate cidata ISO"
        continue

    print "Starting VM using new instance with name %s" % instance_name
    virt_cmd = ['/usr/bin/virt-install', '--import', '--name', instance_name,
                '--ram', '2048', '--disk',
                'path=%s,format=qcow2,bus=virtio' % fp_to_instance,
                '--disk', 'path=%s,device=cdrom' % fp_to_ci_iso,
                '--network', 'bridge=virbr0', '--os-type', 'linux',
                '--os-variant', 'rhel7', '--noautoconsole']
    virt_p = subprocess.Popen(virt_cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    virt_out, virt_err, = virt_p.communicate()
    if virt_p.returncode != 0:
        print virt_err
        continue

    virsh_cmd = ['/usr/bin/virsh', 'dumpxml', instance_name]
    virsh_p = subprocess.Popen(virsh_cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    virsh_out, virsh_err = virsh_p.communicate()
    if virsh_p.returncode != 0:
        print virsh_err
        continue

    mac_re = re.compile(r'mac address=\''
                        r'(?P<mac_address>([0-9a-f]{2}:){5}([0-9a-f]{2}))')
    m = mac_re.search(virsh_out)
    if m is not None:
        mac_addr = m.group('mac_address')
    else:
        print "ERROR: unable to determine MAC address for domain"
        continue

    print "Waiting for ARP table to be populated",
    sys.stdout.flush()
    populated = None
    while populated is None:
        ip_cmd = ['/usr/sbin/ip', 'neigh', 'show', 'dev', 'virbr0']
        ip_p = subprocess.Popen(ip_cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        ip_out, ip_err = ip_p.communicate()
        if ip_p.returncode != 0:
            print ip_err
            continue

        for l in ip_out.split('\n'):
            if mac_addr in l:
                populated = 1
                ip_addr = l.split()[0]

        print ".",
        sys.stdout.flush()
        time.sleep(1)

    print "\n\tMAC Address: %s" % mac_addr
    print "\tIP Address: %s" % ip_addr
