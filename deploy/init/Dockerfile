FROM elasticsearch:5.6.6


# Need python to load sample data into Elasticsearch
RUN apt-get update
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y

RUN python3 --version

RUN pip3 install requests
RUN pip3 install elasticsearch5
RUN pip3 install parse
RUN pip3 install jinja2

# Copy files to container
COPY train /train
COPY deploy/init /train

RUN chown -R elasticsearch:elasticsearch /train

RUN ls /train
WORKDIR /train

RUN ./prepare.sh

CMD /train/init.sh
