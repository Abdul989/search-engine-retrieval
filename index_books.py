import json
import math
from elasticsearch import Elasticsearch, helpers

def create_index(es, index_name):
    """
    Creates an Elasticsearch index with custom settings and mappings.
    Uses Elasticsearch's default BM25 similarity and sets custom boosts for fields.
    """
    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "similarity": {
                "default": {
                    "type": "BM25",
                    "k1": 1.2,
                    "b": 0.75
                }
            }
        },
        "mappings": {
            "properties": {
                "ISBN": {"type": "keyword"},
                "Title": {"type": "text", "analyzer": "standard", "boost": 2},
                "Author": {"type": "text", "analyzer": "standard", "boost": 1.5},
                "Publisher": {"type": "text", "analyzer": "standard"},
                "Description": {"type": "text", "analyzer": "standard"},
                "Search_Text": {"type": "text", "analyzer": "standard"},
                "Num_pages": {"type": "float"},
                "timestamp": {"type": "date", "format": "epoch_second"},
                "Average_Rating": {"type": "float"}
            }
        }
    }
    
    # Delete the index if it exists to start fresh
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Deleted existing index '{index_name}'.")
        
    es.indices.create(index=index_name, body=mapping)
    print(f"Index '{index_name}' created with mapping.")

def load_books(json_file):
    """
    Loads and preprocesses book records from a JSON file.
    Ensures that 'Average_Rating' is a valid float and replaces NaN with 0.0.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for record in data:
        avg = record.get("Average_Rating")
        # If Average_Rating is missing, set to 0.0.
        if avg is None:
            record["Average_Rating"] = 0.0
        else:
            try:
                avg = float(avg)
            except (TypeError, ValueError):
                avg = 0.0
            # Check if the value is NaN. If so, use 0.0 instead.
            if math.isnan(avg):
                avg = 0.0
            record["Average_Rating"] = avg
    return data

def bulk_index(es, index_name, data):
    """
    Bulk indexes the list of book records into Elasticsearch.
    Uses ISBN as the document ID when available.
    """
    actions = []
    for record in data:
        action = {
            "_index": index_name,
            "_id": record.get("ISBN"),
            "_source": record
        }
        actions.append(action)
        
    helpers.bulk(es, actions)
    print(f"Indexed {len(data)} records into '{index_name}'.")

if __name__ == "__main__":
    # Connect to a local Elasticsearch instance (ensure it's running at http://localhost:9200)
    es = Elasticsearch("http://localhost:9200")
    index_name = "books_index"
    
    # Create the index with specified settings and mappings
    create_index(es, index_name)
    
    # Load and preprocess book data from the JSON file
    data = load_books("books.json")
    
    # Bulk index all records into the created index
    bulk_index(es, index_name, data)