#!/usr/bin/env python
#
# Perform multiple rollbacks and record result
#
# Copyright 2015 Micah Abbott <micah@redhat.com>
# Licensed under GPLv2 license (http://opensource.org/licenses/gpl-2.0.php)

import argparse
import paramiko
import re
import time

def get_active_atomic_version(lines):

    status_re = re.compile(r'^\* '
                           r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
                           r' {5}(?P<version>\d+.\d+.\d+(-\d+)?)'
                           r' +(?P<id>\w{10})'
                           r' {5}(?P<osname>[\w\-]+)'
                           r' {5}(?P<refspec>[\w:\-/]+)')

    atomic_version = None
    for l in lines.split('\n'):
        m = status_re.search(l)
        if m:
            atomic_version = m.group('version')

    return atomic_version


parser = argparse.ArgumentParser(prog="rollbacks")
parser.add_argument("--host", help="Remote host", action="store", required=True)
parser.add_argument("-u","--user", help="Remote username", action="store", required=True)
parser.add_argument("-k", "--key", help="Path to SSH private key", action="store", required=False, default=None)
parser.add_argument("-l", "--loops", help="Number of times to perform rollback", action="store", required=False, default=10)
arg = parser.parse_args()

rollback_cmd = "sudo atomic host rollback"
reboot_cmd = "sudo systemctl reboot"
status_cmd = "sudo atomic host status"

# record status of rollback
# record_rollback[n] = ["pre_rollback", "post_rollback", "post_reboot"]
record_rollback = {}

num_loops = 1
while num_loops <= int(arg.loops):
    print "Starting loop %d..." % num_loops
    pre_ssh = paramiko.SSHClient()
    pre_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pre_ssh.connect(hostname=arg.host, username=arg.user, key_filename=arg.key)

    # get active atomic host version
    stdin, stdout, stderr = pre_ssh.exec_command(status_cmd)
    pre_rollback = stdout.read()
    pre_rollback_version = get_active_atomic_version(pre_rollback)
    print "\tActive Version: %s" % pre_rollback_version

    # perform rollback
    stdin, stdout, stderr = pre_ssh.exec_command(rollback_cmd)
    time.sleep(6)

    # get active atomic host version after rollback
    stdin, stdout, stderr = pre_ssh.exec_command(status_cmd)
    post_rollback = stdout.read()
    post_rollback_version = get_active_atomic_version(post_rollback)
    print "\tActive Version After Rollback: %s" % post_rollback_version
    # reboot system
    print "\tRebooting system; sleeping for 20s..."
    stdin, stdout, stderr = pre_ssh.exec_command(reboot_cmd)
    pre_ssh.close()

    time.sleep(20)
    post_ssh = paramiko.SSHClient()
    post_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    post_ssh.connect(hostname=arg.host, username=arg.user, key_filename=arg.key)

    # get active atomic host version after reboot
    stdin, stdout, stderr = post_ssh.exec_command(status_cmd)
    post_reboot = stdout.read()
    post_reboot_version = get_active_atomic_version(post_reboot)
    print "\tActive Version After Reboot: %s" % post_reboot_version
    post_ssh.close()

    record_rollback[num_loops] = [pre_rollback_version, post_rollback_version, post_reboot_version]

    num_loops += 1

print record_rollback