FROM fedora:21
MAINTAINER Micah Abbott <micah@redhat.com>

# Copy Dockerfile to image
COPY Dockerfile /root/

# Update to latest, install some packages, clean up
RUN yum -y update && yum -y install \
    cloud-utils \
    gcc \
    gcc-c++ \
    git \
    libffi-devel \
    python-devel \
    python-pip \
    sudo \
    vim && \
    yum clean all

# Update pip
RUN pip install --upgrade pip

# Checkout internal repos
WORKDIR /root
ENV GIT_SSL_NO_VERIFY=True
RUN git clone https://code.engineering.redhat.com/gerrit/atomic-ci-jobs
RUN git clone https://code.engineering.redhat.com/gerrit/ci-factory

# Checkout GitHub repo
ENV GIT_SSL_NO_VERIFY=False
RUN git clone https://github.com/aweiteka/UATFramework.git

# Install ci-factory bits
WORKDIR /root/ci-factory
RUN ./install.sh

# Install UATFramework requirements
WORKDIR /root/UATFramework
RUN pip install -r requirements.txt

# Setup SSH keys
WORKDIR /root
RUN mkdir /root/.ssh/ && \
    chmod 0700 /root/.ssh && \
    cp /root/ci-factory/targets/keys/ci-ops-central /root/.ssh/id_rsa && \
    chmod 0600 /root/.ssh/id_rsa

# Setup UATFramework to use provisioned resources
RUN ln -s /root/resources.json /root/UATFramework/resources.json && \
    ln -s /root/ci-factory/utils/central_ci_dynamic_hosts.py /root/UATFramework/config/central_ci_dynamic_hosts.py && \ 
    cp /root/atomic-ci-jobs/project/tests/config_data/team6-uat.cfg /root/UATFramework/config/uat.cfg

# Configure QEOS environment variables
ENV OS_AUTH_URL="http://qeos.lab.eng.rdu2.redhat.com:5000/v2.0" 
ENV OS_TENANT_ID="f0269e92050742a3b68fbde6777a3110" 
ENV OS_TENANT_NAME="atomic-e2e-jenkins" 
ENV OS_USERNAME="atomic-e2e-jenkins" 
ENV OS_PASSWORD="changeme"

# Drop into bash
ENTRYPOINT [ "/bin/bash" ]
