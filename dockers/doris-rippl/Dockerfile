# install CONDA
FROM python:3.8.12
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
USER root

RUN apt-get update && apt-get install -y wget git
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b

# # Install RIPPL and its dependencies
RUN echo "hello" 
RUN conda create -n rippl_env
RUN conda config --prepend channels conda-forge
RUN conda config --set channel_priority strict
RUN conda install -n rippl_env utm jupyter requests numpy scipy scikit-image matplotlib fiona shapely cartopy pyproj lxml gdal
RUN activate rippl_env
RUN echo "hello"
# CMD [ "/root/miniconda3/bin/conda" ]

# RUN useradd -ms /bin/bash rippl 
# ENV RIPPL_DIR="/opt/doris_rippl"
# RUN mkdir $RIPPL_DIR \
#     && git clone https://bitbucket.org/grsradartudelft/rippl.git $RIPPL_DIR 
    

# RUN chown -R rippl: $RIPPL_DIR
# USER rippl
# WORKDIR /home/rippl




