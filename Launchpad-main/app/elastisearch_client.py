# Module: app/elastisearch_client.py
# Brief: TODO - add description

ELASTICSEARCH_URL = "http://localhost:9200"
from elasticsearch import Elasticsearch
es = Elasticsearch(ELASTICSEARCH_URL)
INDEX_NAME  = "products"