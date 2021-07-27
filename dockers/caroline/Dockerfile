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

# Install PostgreSQL client
RUN apt-get install -y lsb-release \
    && echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -y postgresql-client-13

# Cleanup apt cache to minimize image size
RUN apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY dockers/caroline/docker-entry-point.d /docker-entry-point.d
COPY dockers/caroline/docker-entry-point.sh /docker-entry-point.sh

# Setup caroline for development
RUN groupadd -r caroline \
    && useradd -m --no-log-init -r -g caroline caroline \
    && mkdir -p /home/caroline/src/caroline \
    && chown -R caroline: /home/caroline/src/caroline

WORKDIR /home/caroline

VOLUME [ "/sys/fs/cgroup" ]

ENTRYPOINT [ "/docker-entry-point.sh" ]
