  function renderResults(data, search, modelName, beforeOrAfter) {
    // handle requested data from server
    var template = document.getElementById('template').innerHTML;
    Mustache.parse(template);   // optional, speeds up future uses
    var rendered = ""; //"<h5>" + search + "</h5>";
    if (beforeOrAfter === 'after') {
      // rendered += "<h3>Learning to Rank Results <small class='text-muted'></br>" + modelName + " model trained with <a href=\"https://github.com/o19s/elasticsearch-ltr-demo/blob/master/train/movie_judgments.txt#L57\">this training data</a></small></h3>"
    } else {
      // rendered += "<h4><small class='text-muted'>Untuned Elasticsearch</small></h4>"
    }
    data.hits.hits.forEach(function (document) {
      rendered = rendered + Mustache.render(template, {doc: document, search: search});
    });
    document.getElementById(beforeOrAfter).innerHTML = rendered;
  };

  //var esUrl = 'http://localhost:9200/tmdb/_search'
  var esUrl = "http://es-for-ltr.labs.o19s.com:7271/tmdb/_search";

  function getExpansions(search, searchField, expandField, shardSize, minDocCount, onDone) {
      body = {
          "size": 0,
          "query": {
              "match": {
              }
          },
          "aggs": {
               "over_top_n" : {
                  "sampler" : {
                      "shard_size" : shardSize
                  },
                  "aggs": {
                      "expansions": {
                          "significant_terms": {
                              "field": expandField,
                              "min_doc_count": minDocCount
                          }
                      }
                  }
               }
          }
      }
      body.query.match[searchField] = search;
      $.ajax({
        method: "GET",
        url: esUrl,
        crossDomain: true,
        async: false,
        data: "source=" + JSON.stringify(body),
        dataType: 'json',
        contentType: 'application/json',
      })
        .done(function (data) {
          // for sigTerm in results['aggregations']['over_top_n']['expansions']['buckets']:
          var rVal = "";
          data.aggregations.over_top_n.expansions.buckets.forEach(function (sigTerm) {

            var term = sigTerm.key;
            var weight = sigTerm.score;

            var multiTerm = term.split(/s+/);
            if (multiTerm.length > 0) {
              var i = 0;
              term = "\"";
              for (i = 0; i < multiTerm.length; i++) {
                term += multiTerm[i] + " ";
              }
              term += "\"";
            }
            rVal += " " + term + "^" + weight;

          });

          onDone(rVal);
        })
  }

  function resultsForAfter() {
    var search = document.getElementById("inputSearch").value;
    getResults(search, 'after');
  }

  function resultsForBefore() {
    var search = document.getElementById("inputSearch").value;
    getResults(search, 'before');
  }

  function resultsForBoth() {
    var search = document.getElementById("inputSearch").value;
    getResults(search, 'after');
    getResults(search, 'before');
  }

  function getResults(search, beforeOrAfter) {
    getExpansions(search, 'text_all', 'text_all.trigramed', 100, 1, (expansionsTextAllTrigrams) => {
          getExpansions(search, 'text_all', 'genre.name', 100, 1, (expansionsGenre) => {

            var data = {
              "query": {
                "multi_match": {
                  "query": search,
                  "fields": ["text_all.en"],
                  "type": "cross_fields"
                }
              },
              "highlight" : {
                  "fields" : {
                      "overview.en" : {}
                  }
              },
              "rescore": {
                "window_size": 500,
                "query": {
                  "query_weight": 1.0,
                  "rescore_query_weight": 100.0,
                  "rescore_query": {
                    "sltr": {
                      "params": {
                        "keywords": search,
                        "expansions_text_all_trigrams": expansionsTextAllTrigrams,
                        "expansions_genre": expansionsGenre,
                      },
                      "model": "test_1"
                    }
                  }
                }
              }
            };
            var model = null;
            if (beforeOrAfter == 'after') {
              switch (true) {
                case document.getElementById('test_6').checked:
                  data.rescore.query.rescore_query.sltr.model = 'test_6';
                  model = "LambdaMART";
                  break;
                case document.getElementById('test_8').checked:
                  data.rescore.query.rescore_query.sltr.model = 'test_8';
                  model = "Random Forest";
                  break;
                case document.getElementById('test_9').checked:
                  data.rescore.query.rescore_query.sltr.model = 'test_9';
                  model = "Linear";
                  break;
                default:
                  delete data.rescore;
              }
            } else {
              delete data.rescore;
            }

            $.ajax({
              method: "GET",
              url: esUrl,
              crossDomain: true,
              async: false,
              data: "source=" + JSON.stringify(data),
              dataType: 'json',
              contentType: 'application/json',
            })
              .done(function (data) {
                renderResults(data, search, model, beforeOrAfter);
              })
              .fail(function (data) {
                console.log(data);
              });


          })

    })

  }

