import sys
from elasticsearch import Elasticsearch

# Configure the boost mode here. Options: "sum", "multiply", "max", etc.
BOOST_MODE = "multiply"  # You can experiment with this value

def search(query, index="books_index", size=50):
    """
    Executes a search against the specified Elasticsearch index using a multi_match query
    with BM25, additional field boosts, and a field value factor on Average_Rating.
    """
    es = Elasticsearch("http://localhost:9200")
    
    body = {
        "query": {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "Title^3",       # Boost the Title field
                            "Author^2",    # Boost the Author field
                            "Publisher",
                            "Description",
                            "Search_Text"
                        ]
                    }
                },
                "field_value_factor": {
                    "field": "Average_Rating",
                    "factor": 0.1,
                    "modifier": "sqrt",  # Adjust using the square-root of the rating
                    "missing": 1         # Default value if the field is missing
                },
                "boost_mode": BOOST_MODE  # Combine the BM25 score and the rating boost
            }
        },
        "size": size
    }
    
    res = es.search(index=index, body=body)
    return res

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_books.py 'your search query'")
        sys.exit(1)
    
    query = sys.argv[1]
    results = search(query)
    
    print("Search Results:")
    for hit in results["hits"]["hits"]:
        source = hit["_source"]
        score = hit["_score"]
        title       = source.get("Title", "N/A")
        author      = source.get("Author", "N/A")
        publisher   = source.get("Publisher", "N/A")
        timestamp   = source.get("timestamp", "N/A")
        rating      = source.get("Average_Rating", "N/A")
        description = source.get("Description", "N/A")
        book_format = source.get("Format", "N/A")
        
        print("-"*50)
        print(f"Title: {title}")
        print(f"Author: {author}")
        print(f"Publisher: {publisher}")
        print(f"Timestamp: {timestamp}")
        print(f"Rating: {rating}")
        print(f"Description: {description}")
        print(f"Format: {book_format}")
        print(f"Score: {score:.2f}\n")