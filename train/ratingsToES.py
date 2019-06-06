import json

from elasticsearch5 import Elasticsearch, helpers
movieLensPath = 'ml-20m/ratings.csv'

def movieLensRatings():
    import csv
    ml_ratings_f = open(movieLensPath)
    ml_reader = csv.reader(ml_ratings_f, delimiter=',')
    for rowNo, row in enumerate(ml_reader):
        try:
            yield (int(row[0]), int(row[1]), float(row[2]), int(row[3]))
        except ValueError:
            if rowNo == 0:
                print("Skipping CSV header")
            else:
                raise

def userBaskets(minRating=4):
    """ Movies a given user likes """
    # Assumes sorted by user id
    print("Buliding baskets")
    lastUserId = -1
    basket = []
    for userId, itemId, rating, timestamp in movieLensRatings():
        if userId != lastUserId:
            lastUserId = userId
            if len(basket) > 0:
                yield {"_index": "movielens", "_type": "user",
                        "_id": lastUserId, "_source": {"liked_movies": basket}}
            basket = []
        if rating >= minRating:
            basket.append(str(itemId))


def indexToElastic(es):
    analysisSettings = {}
    index = 'movielens'

    settings = { #A
        "settings": {
            "number_of_shards": 1, #B
            "index": {
                "analysis" : analysisSettings, #C
            }}}

    es.indices.delete(index, ignore=[400, 404])
    es.indices.create(index, body=json.dumps(settings))

    helpers.bulk(es, userBaskets(), chunk_size=250)


if __name__ == "__main__":
    from sys import argv
    es_url = argv[1]

    es = Elasticsearch(es_url)
    indexToElastic(es)

