FROM rhel7/rhel-tools
MAINTAINER Micah Abbott <micah@redhat.com>
ENV container docker
RUN yum --disablerepo=\* --enablerepo=rhel-7-server-rpms install -y yum-utils
RUN yum-config-manager --disable \*
RUN yum-config-manager --enable rhel-7-server-rpms
RUN yum -y update; yum clean all
WORKDIR /var/qe
CMD ["git","clone","https://github.com/miabbott/utils.git"]
LABEL INSTALL='mkdir -p /var/qe; chcon -Rt svirt_sandbox_file_t /var/qe'
LABEL RUN='docker run --rm -v /var/qe:/var/qe -e IMAGE=IMAGE -e NAME=NAME IMAGE'