# Oil Database Docker configuration
#

FROM gitlab.orr.noaa.gov:5002/centos-conda
RUN yum update -y

COPY ./ /oil-database/

RUN cd oil-database/oil_db && conda install --file conda_requirements.txt
RUN cd oil-database/oil_db && pip install -r pip_requirements.txt
RUN cd oil-database/oil_db && python setup.py develop

RUN cd oil-database/oil_db && yes | oil_db_init
RUN cd oil-database/oil_db && oil_db_import --all


EXPOSE 27017
VOLUME /config
ENTRYPOINT ["/oil-database/docker_start.sh"] 
