from esUrlParse import parseUrl
from judgments import Judgment, judgmentsFromFile, judgmentsToFile
from elasticsearch import Elasticsearch, TransportError
import json

def formatSearch(keywords):
    from jinja2 import Template
    template = Template(open("rateSearch.json.jinja").read())
    jsonStr = template.render(keywords=keywords)
    return json.loads(jsonStr)

def getPotentialResults(esUrl, keywords):
    (esUrl, index, searchType) = parseUrl(esUrl)
    es = Elasticsearch(esUrl)

    query = formatSearch(keywords)
    try:
        print("Query %s" % json.dumps(query))
        results = es.search(index=index, body=query)
        return results['hits']['hits']
    except TransportError as e:
        print("Query %s" % json.dumps(query))
        print("Query Error: %s " % e.error)
        print("More Info  : %s " % e.info)
        raise e



def gradeResults(results, keywords, qid):
    titleField = 'title'
    overviewField = 'overview'
    ratings = []
    print("Rating %s results" % len(results))
    for result in results:
        grade = None
        if 'fields' not in result:
            if '_source' in result:
                result['fields'] = result['_source']
        if 'fields' in result:
            print("")
            print("")
            print("## %s " % result['fields'][titleField])
            print("")
            print("   %s " % result['fields'][overviewField])
            while grade not in ["0", "1", "2", "3", "4"]:
                grade = input("Rate this shiznit (0-4) ")
            judgment = Judgment(int(grade), qid=qid, keywords=keywords, docId=result['_id'])
            ratings.append(judgment)

    return ratings



if __name__ == "__main__":
    """ Usage python rateShit.py esURL ratingsFileName """
    from sys import argv

    judgFile = argv[2]

    currJudgments = []
    existingKws = set()
    lastQid = 0
    try:
        currJudgments = [judg for judg in judgmentsFromFile(judgFile)]
        existingKws = set([judg.keywords for judg in currJudgments])
        lastQid = currJudgments[-1].qid
    except FileNotFoundError:
        pass


    keywords = "-"
    qid = lastQid + 1
    while len(keywords) > 0:
        keywords = input("Enter the Keywords ('GTFO' to exit) ")

        if keywords == "GTFO":
            break

        if keywords in existingKws:
            print ("Sorry, we already have ratings for %s. Try again" % keywords)
        else:
            results = getPotentialResults(argv[1], keywords)
            ratings = gradeResults(results, keywords, qid)
            currJudgments += ratings

            qid += 1

    judgmentsToFile(judgFile, currJudgments)
