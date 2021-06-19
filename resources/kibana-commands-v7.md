# Kibana commands

- You can use the [Dev Tools](http://localhost:5601/app/dev_tools#/console) in Kibana to use these commands.
- Or you can use the command-line using the format: `curl -X <TYPE> "http://localhost:9200<endpoint>"`
    - e.g. `curl -X GET "http://localhost:9200/_cat/indices/t*"`

## Indices

### View existing indices by index pattern (you can also use regex)
`GET /_cat/indices/<index-pattern>`

### View the mapping of the index
`GET <index-name>/_mapping`

### Create index
This is handled in-code, but if you'd like to test the index mapping you're using:
```shell
PUT <index-name>
<index-mapping>
```

### Delete an index
`DELETE /<index-name>`

### Change index name (reindex)
```shell
POST _reindex
{
  "source":{
    "index": "<index-name>"
  },
  "dest": {
    "index": "<new-index-name>"
  }
}
```

## HCVA

### Searching
```shell
POST <index-name>/_search
{
  "query": {
    "multi_match": {
      "query": "<hebrew-word>",
      "fields": [
        "*"
      ]
    }
  }
}
```


## Plugin

### View the root of the word
`GET /_hebrew/check-word/<hebrew-word>`

### Testing
```shell
PUT test-plugin
{
  "mappings": {
    "properties": {
      "content": {
        "type": "text",
        "analyzer": "hebrew"
      }
    }
  }
}
```

```shell
PUT test-plugin/_doc/1
{
    "content": "שיעול והקאות וביום 14.2.91 אובחנה אצלו דלקת ריאות. בחודש אוקטובר 1991 הוא אושפז שוב עקב דלקת ריאות ואובחנה אצלו מחלה של חסר חיסוני"
}
```

```shell
POST test-plugin/_search
{
    "query": {
    "multi_match": {
      "query": "אובחן",
      "fields": [
        "*"
      ]
    }
  }
}
```