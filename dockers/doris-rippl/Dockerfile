# install CONDA
FROM python:3.8.12
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
USER root

RUN apt-get update && apt-get install -y wget git
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b

# # Install RIPPL and its dependencies in a new environment
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL [ "conda", "run", "-n", "rippl_env", "/bin/bash", "-c" ]

# Clone Doris-Rippl
ENV RIPPL_DIR="/opt/doris_rippl"
RUN mkdir $RIPPL_DIR \
    && git clone https://bitbucket.org/grsradartudelft/rippl.git $RIPPL_DIR 


RUN useradd -ms /bin/bash rippl 
RUN chown -R rippl: $RIPPL_DIR
WORKDIR /home/rippl

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "rippl_env", "python"]




