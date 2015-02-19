#!/usr/bin/env python

import os
import subprocess

REPOSDIR = '/home/miabbott/workspaces/rhel-atomic-host'
REPONAME = 'atomic-rhel-7.1-image-build'
GIT_REPO = 'https://code.engineering.redhat.com/gerrit/p/rhel-atomic-host.git'
DATA_DIR = '/var/qe'

# YUM_CMD = 'yum --setopt=reposdir=%s --disablerepo=* --enablerepo=%s info' % (REPOSDIR, REPONAME)
# chcon -Rt svirt_sandbox_file_t /var/qe

# Name        : zziplib-utils
# Arch        : x86_64
# Version     : 0.13.62
# Release     : 5.el7

# if not os.path.isdir(DATA_DIR):
#    assert os.mkdir(DATA_DIR)
#
# assert subprocess.check_call('chcon', '-Rt', 'svirt_sandbox_file_t', DATA_DIR)

yum_output = subprocess.check_output(['yum', '--setopt=reposdir=%s' % REPOSDIR, '--disablerepo=*', '--enablerepo=%s' % REPONAME, 'info'])

yum_lines = yum_output.split('\n')

package_vars = []
package_list = []
for line in yum_output.split('\n'):
    line_split = line.split(':')
    if 'Name        ' in line_split:
        package_vars.append(line_split[1].strip())
    if 'Arch        ' in line_split:
        package_vars.append(line_split[1].strip())
    if 'Version     ' in line_split:
        package_vars.append(line_split[1].strip())
    if 'Release     ' in line_split:
        package_vars.append(line_split[1].strip())
        package_list.append(package_vars[0] + '-' + package_vars[2] + '-' + package_vars[3] + '.' + package_vars[1])
        package_vars = []

rpm_output = subprocess.check_output(['rpm', '-qa'])

for rpm in rpm_output.split('\n'):
    assert rpm not in package_list