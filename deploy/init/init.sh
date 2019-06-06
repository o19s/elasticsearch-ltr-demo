#!/bin/bash

sleep 15

echo "Going to load data into Elasticsearch"


echo "Running indexMlTmdb.py"
python3 /train/indexMlTmdb.py http://elasticsearch:9200

echo "Running ratingsToES.py"
python3 /train/ratingsToES.py http://elasticsearch:9200

echo "Running train.py"
python3 /train/train.py http://elasticsearch:9200


echo "Done with setup"
