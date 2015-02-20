#!/bin/bash

SERVICEFILE='/etc/systemd/system/multi-user.target.wants/python-echo.service'
ECHODIR='/var/opt/python-echo/'
DOCKERFILE='/var/opt/python-echo/Dockerfile'
ECHOFILE='/var/opt/python-echo/echo.py'

if [ ! -f "$SERVICEFILE" ] ; then
	touch "$SERVICEFILE"
fi

if [ ! -d "$ECHODIR" ] ; then
	mkdir -p "$ECHODIR"
fi

if [ ! -f "$DOCKERFILE" ] ; then
	touch "$DOCKERFILE"
fi

if [ ! -f "$ECHOFILE" ] ; then
	touch "$ECHOFILE"
fi

cat > "$SERVICEFILE" << EOF
[Unit]
Description=Python Echo App
Author=Micah Abbott <miabbott@redhat.com>
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
ExecStartPre=-/usr/bin/docker kill python-echo
ExecStartPre=-/usr/bin/docker rm python-echo
ExecStartPre=/usr/bin/docker build -t miabbott/python-echo /var/opt/python-echo/
ExecStart=/usr/bin/docker run --name=python-echo miabbott/python-echo
ExecStop=-/usr/bin/docker stop python-echo

[Install]
WantedBy=multi-user.target
EOF

cat > "$ECHOFILE" << EOF
#!/usr/bin/env python
import os

print "First Name: " + os.environ['firstName']
print "Last Name: " + os.environ['lastName']
print "Company: " + os.environ['company']
print "Org: " + os.environ['org']
print "Project: " + os.environ['project']

EOF

cat > "$DOCKERFILE" << EOF
FROM rhel7
MAINTAINER Micah Abbott <miabbott@redhat.com>
ADD echo.py /usr/local/bin/echo.py
RUN chmod +x /usr/local/bin/echo.py
ENV firstName Micah 
ENV lastName Abbott 
ENV company RedHat 
ENV org QE 
ENV project Atomic
ENTRYPOINT ["/usr/local/bin/echo.py"]
EOF

systemctl daemon-reload
