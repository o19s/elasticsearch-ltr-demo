#!/bin/bash
if [ ${ELASTICSEARCH_URL+x} ]
then ELASTICSEARCH_URL=$ELASTICSEARCH_URL
else ELASTICSEARCH_URL=http://localhost:9200
fi

sed -i -e "s,DYN_ELASTICSEARCH_URL,$ELASTICSEARCH_URL,g" ./search*.js

python -m SimpleHTTPServer
