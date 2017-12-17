import json
from elasticsearch import Elasticsearch
from elasticsearch import TransportError

def formatExpansion(keywords, minDocCount=3, searchField='text_all', expandField='text_all', shardSize=100):
    from jinja2 import Template
    template = Template(open("gatherExpansion.json.jinja").read())
    jsonStr = template.render(keywords=keywords,
                              minDocCount=minDocCount,
                              searchField=searchField,
                              expandField=expandField,
                              shardSize=shardSize)
    return json.loads(jsonStr)


def getExpansions(es, keywords, minDocCount=3, searchField='text_all', expandField='text_all',
                  shardSize=100, index='tmdb'):
    query = formatExpansion(keywords, minDocCount=minDocCount, searchField=searchField, expandField=expandField,
                            shardSize=shardSize)
    try:
        print("Query %s" % json.dumps(query))
        results = es.search(index=index, body=query)
        rVal = ""
        for sigTerm in results['aggregations']['over_top_n']['expansions']['buckets']:
            term = sigTerm['key']
            multiTerm = term.split()
            if len(multiTerm) > 1:
                term = '"' + " ".join(multiTerm) + '"'
            rVal += " %s^%s" % (term, sigTerm['score'])
        return rVal

    except TransportError as e:
        print("Query %s" % json.dumps(query))
        print("Query Error: %s " % e.error)
        print("More Info  : %s " % e.info)
        raise e

def expansionTextAllBigrams(es, keywords):
    return getExpansions(es, keywords, expandField='text_all.bigramed', minDocCount=1)

def expansionTextAll(es, keywords):
    return getExpansions(es, keywords, expandField='text_all', minDocCount=1)

def expansionTitle(es, keywords):
    return getExpansions(es, keywords, expandField='title', minDocCount=1)

def expansionGenre(es, keywords):
    return getExpansions(es, keywords, expandField='genre.name', minDocCount=1)

if __name__ == "__main__":
    from sys import argv
    import configparser
    config = configparser.ConfigParser()
    config.read('settings.cfg')
    esUrl = config['DEFAULT']['ESHost']

    es = Elasticsearch(esUrl, timeout=1000)
    print(getExpansions(es, argv[1], expandField="text_all.bigramed"))
