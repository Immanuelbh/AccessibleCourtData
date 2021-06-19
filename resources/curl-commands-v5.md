### -------------------------------- ELK_5.5.3 --------------------------------

`curl -i -XPOST --user 'elastic:changeme' 'http://localhost:9200/supreme_court/rulings/test?pretty' --data-ascii '@19-03-2020_12-50-44.json' -H 'Content-Type:application/json'`

`curl -X GET --user 'elastic:changeme' 'http://localhost:9200/supreme_court/rulings/test'`

`curl -X DELETE --user 'elastic:changeme' 'http://localhost:9200/supreme_court'`


### -------------------------------- ELK_5.5.3 Tests --------------------------------

`curl -i -XPUT --user 'elastic:changeme' 'http://localhost:9200/supreme_court_rulings'`

`curl -i -XPUT --user 'elastic:changeme' 'http://localhost:9200/supreme_court_rulings' -d '{"mappings": {"test": {"properties": {"content": {"type": "text","analyzer": "hebrew_query"}}}}}'`

`curl -XPOST --user 'elastic:changeme' localhost:9200/supreme_court_rulings/_close`

`curl -i -XPOST --user 'elastic:changeme' localhost:9200/supreme_court_rulings/_mapping -d '{"properties":{"description":{"type":"text", "analyzer":"hebrew_query"}}}'`

`curl -XPOST --user 'elastic:changeme' localhost:9200/supreme_court_rulings/_open`

`curl -X DELETE --user 'elastic:changeme' 'http://localhost:9200/supreme_court_rulings'`

`curl -i -XGET --user 'elastic:changeme' 'http://localhost:9200/supreme_court_rulings/_mapping'`

`curl -i -XPOST --user 'elastic:changeme' 'http://localhost:9200/supreme_court_rulings/_mapping' -d '{"properties":{"description":{"type":"text", "analyzer":"hebrew_query"}}}' -H 'Content-Type:application/json'`

### -------------------------------- Elasticsearch + Kibana 5.5.3 --------------------------------

`GET /_cat/indices?pretty`

`GET supreme_court`

`GET supreme_court_hebrew`

```shell
POST _reindex
{
  "source":{
    "index": "supreme_court"
  },
  "dest": {
    "index": "supreme_court_hebrew"
  }
}
```

```shell
PUT supreme_court_hebrew
{
  "mappings": {
    "rulings": {
      "properties": {
        "doc": {
          "properties": {
            "Case Details": {
              "properties": {
                "אירועים": {
                  "properties": {
                    "#": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "ארוע משני": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "ארוע ראשי": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "יוזם": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "תאריך": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "אישורי מסירה": {
                  "properties": {
                    "#": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "נמען": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "תאריך חתימה": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "בקשות": {
                  "properties": {
                    "#": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "מגיש": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "נדחה מהמרשם": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "תאריך": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "תיאור בקשה": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "דיונים": {
                  "properties": {
                    "אולם": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "גורם שיפוטי": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "סטטוס": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "שעת דיון": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "תאריך": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "פרטים כלליים": {
                  "properties": {
                    "אירוע אחרון": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "מדור": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "מספר הליך": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "מערער": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "משיב": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "סטטוס תיק": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "תאריך הגשה": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "צדדים בתיק": {
                  "properties": {
                    "#": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "באי כוח": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "סוג צד": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "שם": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "תיק דלמטה": {
                  "properties": {
                    "הרכב/שופט": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "מספר תיק דלמטה": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "שם בית המשפט": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "ת": {
                      "properties": {
                        "החלטה": {
                          "type": "text",
                          "analyzer": "hebrew",
                          "fields": {
                            "keyword": {
                              "type": "keyword",
                              "ignore_above": 256
                            }
                          }
                        }
                      }
                    },
                    "תאריך החלטה": {
                      "type": "text",
                      "analyzer": "hebrew",
                      "fields": {
                        "keyword": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                }
              }
            },
            "Doc Details": {
              "properties": {
                "null": {
                  "type": "text",
                  "analyzer": "hebrew",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "בשם המשיב": {
                  "type": "text",
                  "analyzer": "hebrew",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "בשם העותר": {
                  "type": "text",
                  "analyzer": "hebrew",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "המשיב": {
                  "type": "text",
                  "analyzer": "hebrew",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "העותר": {
                  "type": "text",
                  "analyzer": "hebrew",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "לפני": {
                  "type": "text",
                  "analyzer": "hebrew",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "מידע נוסף": {
                  "type": "text",
                  "analyzer": "hebrew",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "מספר הליך": {
                  "type": "text",
                  "analyzer": "hebrew",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "סוג מסמך": {
                  "type": "text",
                  "analyzer": "hebrew",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "סיכום": {
                  "type": "text",
                  "analyzer": "hebrew",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                }
              }
            }
          }
        },
        "doc_as_upsert": {
          "type": "boolean"
        }
      }
    }
  }
}



```


```shell
GET supreme_court_hebrew/_search
{
  "query": {
    "match": {
      "doc.Doc Details.לפני": "שופטים"
    }
  }
}
```
```shell
GET supreme_court_hebrew/_search
{
  "query": {
    "match": {
      "_all": "שופטים"
    }
  }
}
```

```shell
GET supreme_court_hebrew/_search
{
  "query": {
    "multi_match": {
      "query": "שופטים",
      "fields": ["doc.Doc Details.לפני","doc.Case Details.צדדים בת.#"]
    }
  }
}
```

