FROM elasticsearch:5.6.6

# Need python to load sample data into Elasticsearch
#RUN apt-get update
#RUN apt-get install python -y
#RUN apt-get install python-pip -y
#RUN pip install elasticsearch

# Copy data prepped files to host
#COPY etl /etl

# Copy over CORS enabled configuration
ADD ./deploy/elasticsearch/elasticsearch.yml /usr/share/elasticsearch/config/

# Need some plugins!
RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install http://es-learn-to-rank.labs.o19s.com/ltr-1.0.0-es5.6.6.zip -b

EXPOSE 9200
EXPOSE 9300
