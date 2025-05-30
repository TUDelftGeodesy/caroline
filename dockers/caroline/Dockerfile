FROM python:3.9.6

ENV LC_ALL C
ENV DEBIAN_FRONTEND noninteractive

# Setup systemd
RUN apt-get update \
    && apt-get install -y systemd systemd-sysv

RUN rm -f /lib/systemd/system/multi-user.target.wants/* \
    /etc/systemd/system/*.wants/* \
    /lib/systemd/system/local-fs.target.wants/* \
    /lib/systemd/system/sockets.target.wants/*udev* \
    /lib/systemd/system/sockets.target.wants/*initctl* \
    /lib/systemd/system/sysinit.target.wants/systemd-tmpfiles-setup* \
    /lib/systemd/system/systemd-update-utmp*

# Cleanup apt cache to minimize image size
RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install caroline package
COPY . /usr/src/caroline

RUN (cd /usr/src/caroline; python setup.py install)

RUN groupadd -r caroline \
    && useradd -m --no-log-init -r -g caroline caroline

WORKDIR /home/caroline

VOLUME [ "/sys/fs/cgroup" ]

CMD [ "/lib/systemd/systemd" ]
