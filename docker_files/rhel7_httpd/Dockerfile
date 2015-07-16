FROM rhel7
MAINTAINER Micah Abbott <micah@redhat.com>
RUN yum --disablerepo=\* --enablerepo=rhel-7-server-rpms install -y yum-utils
RUN yum-config-manager --disable \*
RUN yum-config-manager --enable rhel-7-server-rpms
RUN yum update -y; yum install -y httpd; yum clean all
EXPOSE 80
ENTRYPOINT [ "/usr/sbin/httpd" ]
CMD [ "-D", "FOREGROUND" ]
