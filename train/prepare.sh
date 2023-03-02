#!/bin/bash
wget https://repo1.maven.org/maven2/com/o19s/RankyMcRankFace/0.1.1/RankyMcRankFace-0.1.1.jar
curl -L -o tmdb.json http://es-learn-to-rank.labs.o19s.com/tmdb_ai_pow_search.json
curl -L -o movie_judgements.txt http://es-learn-to-rank.labs.o19s.com/ai_pow_search_judgments.txt
wget http://files.grouplens.org/datasets/movielens/ml-20m.zip
unzip ml-20m.zip
