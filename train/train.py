import os
from collectFeatures import logFeatures, buildFeaturesJudgmentsFile
from loadFeatures import initDefaultStore, loadFeatures


def trainModel(trainingData, testData, modelOutput, whichModel=8):
    # java -jar RankLib-2.6.jar  -metric2t NDCG@4 -ranker 6 -kcv -train osc_judgments_wfeatures_train.txt -test osc_judgments_wfeatures_test.txt -save model.txt

    # For random forest
    # - bags of LambdaMART models
    #  - each is trained against a proportion of the training data (-srate)
    #  - each is trained using a subset of the features (-frate)
    #  - each can be either a MART or LambdaMART model (-rtype 6 lambda mart)
    cmd = "java -jar RankyMcRankFace-0.1.1.jar -metric2t NDCG@10 -bag 10 -srate 0.6 -frate 0.6 -rtype 6 -shrinkage 0.1 -tree 80 -ranker %s -train %s -test %s -save %s -feature features.txt" % (whichModel, trainingData, testData, modelOutput)
    print("*********************************************************************")
    print("*********************************************************************")
    print("Running %s" % cmd)
    os.system(cmd)
    pass


def partitionJudgments(judgments, testProportion=0.1):
    testJudgments = {}
    trainJudgments = {}
    from random import random
    for qid, judgment in judgments.items():
        draw = random()
        if draw <= testProportion:
            testJudgments[qid] = judgment
        else:
            trainJudgments[qid] = judgment

    return (trainJudgments, testJudgments)



def saveModel(esHost, scriptName, featureSet, modelFname):
    """ Save the ranklib model in Elasticsearch """
    import requests
    import json
    from urllib.parse import urljoin
    modelPayload = {
        "model": {
            "name": scriptName,
            "model": {
                "type": "model/ranklib",
                "definition": {
                }
            }
        }
    }

    # Force the model cache to rebuild
    path = "_ltr/_clearcache"
    fullPath = urljoin(esHost, path)
    print("POST %s" % fullPath)
    resp = requests.post(fullPath)
    if (resp.status_code >= 300):
        print(resp.text)

    with open(modelFname) as modelFile:
        modelContent = modelFile.read()
        path = "_ltr/_featureset/%s/_createmodel" % featureSet
        fullPath = urljoin(esHost, path)
        modelPayload['model']['model']['definition'] = modelContent
        print("POST %s" % fullPath)
        resp = requests.post(fullPath, json.dumps(modelPayload))
        print(resp.status_code)
        if (resp.status_code >= 300):
            print(resp.text)





if __name__ == "__main__":

    HUMAN_JUDGMENTS = 'movie_judgments.txt'
    TRAIN_JUDGMENTS = 'movie_judgments_wfeatures_train.txt'
    TEST_JUDGMENTS = 'movie_judgments_wfeatures_test.txt'

    import configparser
    from elasticsearch5 import Elasticsearch
    from sys import argv
    from judgments import judgmentsFromFile, judgmentsByQid, duplicateJudgmentsByWeight

    config = configparser.ConfigParser()
    config.read('settings.cfg')
    esUrl = config['DEFAULT']['ESHost']
    if len(argv) > 1:
        esUrl = argv[1]

    es = Elasticsearch(esUrl, timeout=1000)


    # Load features into Elasticsearch
    initDefaultStore(esUrl)
    loadFeatures(esUrl)
    # Parse a judgments
    movieJudgments = judgmentsByQid(judgmentsFromFile(filename=HUMAN_JUDGMENTS))
    movieJudgments = duplicateJudgmentsByWeight(movieJudgments)
    trainJudgments, testJudgments = partitionJudgments(movieJudgments, testProportion=0.0)

    # Use proposed Elasticsearch queries (1.json.jinja ... N.json.jinja) to generate a training set
    # output as "sample_judgments_wfeatures.txt"
    logFeatures(es, judgmentsByQid=movieJudgments)

    buildFeaturesJudgmentsFile(trainJudgments, filename=TRAIN_JUDGMENTS)
    buildFeaturesJudgmentsFile(testJudgments, filename=TEST_JUDGMENTS)

    # Train each ranklib model type
    for modelType in [8,9,6]:
        # 0, MART
        # 1, RankNet
        # 2, RankBoost
        # 3, AdaRank
        # 4, coord Ascent
        # 6, LambdaMART
        # 7, ListNET
        # 8, Random Forests
        # 9, Linear Regression
        print("*** Training %s " % modelType)
        trainModel(trainingData=TRAIN_JUDGMENTS, testData=TEST_JUDGMENTS, modelOutput='model.txt', whichModel=modelType)
        saveModel(esHost=esUrl, scriptName="test_%s" % modelType, featureSet='movie_features', modelFname='model.txt')
