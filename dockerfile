# Oil Database Docker configuration
#

FROM gitlab.orr.noaa.gov:5002/centos-conda

COPY ./ /oil-database/

RUN yum update -y
RUN yum install -y redis

RUN cp /oil-database/platform/centos/mongodb-org-4.2.repo /etc/yum.repos.d
RUN yum install mongodb-org -y

RUN cd oil-database/oil_db && conda install --file conda_requirements.txt
RUN cd oil-database/oil_db && pip install -r pip_requirements.txt
RUN cd oil-database/oil_db && python setup.py develop

RUN cd oil-database/oil_db && oil_db_init
RUN cd oil-database/oil_db && oil_db_import --all

RUN cd oil-database/web_api && conda install --file conda_requirements.txt
RUN cd oil-database/web_api && pip install -r pip_requirements.txt
RUN cd oil-database/web_api && python setup.py develop

RUN mkdir /config
RUN cp /oil-database/web_api/config-example.ini /config/config.ini

EXPOSE 9898
VOLUME /config
ENTRYPOINT ["/oil-database/docker_start.sh"] 
