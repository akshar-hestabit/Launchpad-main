# Module: app/elastisearch_client.py


ELASTICSEARCH_URL = "http://localhost:9200"
from elasticsearch import Elasticsearch
es = Elasticsearch(ELASTICSEARCH_URL)
INDEX_NAME  = "products"