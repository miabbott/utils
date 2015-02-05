#!/usr/bin/env python
'''
This helper script performs the following:

1) Scrapes a URL looking for QCOW images
2) Checks an OpenStack instance if the images have been uploaded
3) Downloads the images locally, if not on OpenStack
4) Uploads the image via Glance

Requirements
-------------
beautifulsoup4
python-glanceclient==0.13.1
python-keystoneclient
python-novaclient
requests

Assumptions
------------
* Your OpenStack instance is using v1 of the Glance API
* You have the necessary OpenStack environment variables configured

Good luck!  Have fun!
'''
import gzip
import os
from os import environ as env
import re
import requests
import sys
import urllib

import bs4

import keystoneclient.v2_0.client as ksclient
import glanceclient as glclient
import novaclient.v1_1.client as nvclient

# the list of OpenStack environment variables that need to be set
openstack_envs = ['OS_AUTH_URL',
                  'OS_USERNAME',
                  'OS_PASSWORD',
                  'OS_TENANT_NAME']


# helper method to search for links
def search_links(soup=None, regex=None):
    valid_links = []
    for link in soup.find_all('a'):
        a_href = link.get('href')
        if regex.search(a_href):
            valid_links.append(a_href)

    return valid_links

# check to see if OpenStack env_vars are set
for os_env in openstack_envs:
    assert os.getenv(os_env) is not None

# try to create a Keystone client
try:
    keystone = ksclient.Client(auth_url=env['OS_AUTH_URL'],
                               username=env['OS_USERNAME'],
                               password=env['OS_PASSWORD'],
                               tenant_name=env['OS_TENANT_NAME'])
except:
    sys.exit("Unable to authenticate with Keystone")

# try to create a Glance client
glance_endpoint = keystone.service_catalog.url_for(service_type='image',
                                                   endpoint_type='publicURL')
try:
    glance = glclient.Client('1', glance_endpoint, token=keystone.auth_token)
except:
    sys.exit("Unable to instantiate a Glance client")

# try to create a Nova client
try:
    nova = nvclient.Client(auth_url=env['OS_AUTH_URL'],
                           username=env['OS_USERNAME'],
                           api_key=env['OS_PASSWORD'],
                           project_id=env['OS_TENANT_NAME'])
except:
    sys.exit("Unable to instantiate Nova client")

# set the base URL to look for images
base_url = '<CHANGE_THIS>'

# regex to find date-stamped dirs
# example: 20150115.1
dirs_re = re.compile('\d{8}\.\d')

# regex to search for QCOW2 images
# example: rhel-atomic-host-7.qcow2.gz
qcow_re = re.compile('rhel-atomic-host-7\.(qcow2|qcow2\.gz)')

# initial request of the base URL.  pass it to BeautifulSoup
base_resp = requests.get(base_url)
base_soup = bs4.BeautifulSoup(base_resp.text)

valid_dirs = search_links(soup=base_soup, regex=dirs_re)

# work through the directories and build URLs to investigate
qcow_links = {}
for dir_name in valid_dirs:
    dir_url = base_url + dir_name + 'cloud/'
    dir_resp = requests.get(dir_url)
    dir_soup = bs4.BeautifulSoup(dir_resp.text)

    qcow = search_links(soup=dir_soup, regex=qcow_re)
    qcow_url = dir_url + qcow[0]
    qcow_image_name = 'rhel-atomic-host-7.1-' + dir_name.strip('/')
    qcow_links[qcow_image_name] = qcow_url

# work through the dictionary of image names and associated URLs
for name, url in qcow_links.iteritems():
    try:
        qcow_image = nova.images.find(name=name)
        print "Found image with name: " + name
        continue
    except:
        print "Did not find image with name: " + name

    if ".gz" in url:
        dest_file = "/tmp/" + name + ".qcow2.gz"
    else:
        dest_file = "/tmp/" + name + ".qcow2"

    # Download the file to the local filesystem
    print "Downloading to: " + dest_file
    dl_image = urllib.URLopener()
    dl_image.retrieve(url, dest_file)

    # If the file is gzipped, uncompress it to a new file and delete the .gz
    if ".gz" in dest_file:
        print "Gunzipping: " + dest_file
        qcow_file = dest_file.strip('.gz')
        gz_file_h = gzip.open(dest_file, 'rb')
        qcow_file_h = open(qcow_file, 'wb')
        qcow_file_h.write(gz_file_h.read())
        gz_file_h.close()
        qcow_file_h.close()
        os.remove(dest_file)
    else:
        qcow_file = dest_file

    # With the QCOW2 file ready, open it and upload via glance
    print "Uploading %s via Glance" % name
    with open(qcow_file) as glance_image:
        glance.images.create(name=name,
                             disk_format='qcow2',
                             container_format='bare',
                             data=glance_image)

    # afterwards delete the QCOW2 file from the filesystem
    os.remove(qcow_file)
