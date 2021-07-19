FROM python:3.9.6

#ENV container docker
ENV LC_ALL C
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update     && apt-get install -y systemd systemd-sysv     && apt-get clean     && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* # buildkit

RUN rm -f /lib/systemd/system/multi-user.target.wants/*     /etc/systemd/system/*.wants/*     /lib/systemd/system/local-fs.target.wants/*     /lib/systemd/system/sockets.target.wants/*udev*     /lib/systemd/system/sockets.target.wants/*initctl*     /lib/systemd/system/sysinit.target.wants/systemd-tmpfiles-setup*     /lib/systemd/system/systemd-update-utmp* # buildkit

RUN groupadd -r caroline && useradd -m --no-log-init -r -g caroline caroline

RUN mkdir /home/caroline/caroline

RUN chown -R caroline: /home/caroline/caroline

WORKDIR /home/caroline

USER caroline

VOLUME [ "/sys/fs/cgroup" ]

CMD [ "/lib/systemd/systemd", "--user" ]
