import json
import warnings
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchWarning

# Suppress specific warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ElasticsearchWarning)

def search_books(user_query, size=100):
    """
    Search books using a multi_match query across Title, Author, Publisher.
    Hybrid Sort: Relevance → Average Rating → Latest Timestamp.
    """
    if not user_query:
        print("\nError: Search query cannot be empty.")
        return []

    es = Elasticsearch("http://localhost:9200")
    index_name = "books_index"  # default index name

    query_body = {
        "query": {
            "multi_match": {
                "query": user_query,
                "fields": ["Title^2", "Author^1.5", "Publisher"]
            }
        },
        "_source": [
            "ISBN", "Title", "Author", "timestamp", "Publisher",
            "Description", "Format", "Num_pages", "Average_Rating"
        ],
        "sort": [
            "_score",
            {"Average_Rating": {"order": "desc"}},
            {"timestamp": {"order": "desc"}}
        ]
    }

    response = es.search(index=index_name, body=query_body, size=size)
    results = [hit['_source'] for hit in response['hits']['hits']]
    return results


def display_book(book, idx):
    print(f"Result {idx}:")
    print(f"ISBN: {book.get('ISBN', 'N/A')}")
    print(f"Title: {book.get('Title', 'N/A')}")
    print(f"Author: {book.get('Author', 'N/A')}")
    print(f"Publisher: {book.get('Publisher', 'N/A')}")
    print(f"Description: {book.get('Description', 'N/A')}")
    print(f"Format: {book.get('Format', 'N/A')}")
    print(f"Number of Pages: {book.get('Num_pages', 'N/A')}")
    print(f"Average Rating: {book.get('Average_Rating', 'N/A')}")
    print(f"Timestamp: {book.get('timestamp', 'N/A')}")
    print("-" * 50)


if __name__ == "__main__":
    print("\n--- Book Search ---")
    user_query = input("Enter book info (title, author, or publisher): ").strip()

    print("\nSearching books...\n")

    results = search_books(user_query)  

    if results:
        print(f"Found {len(results)} result(s):\n")
        for idx, book in enumerate(results, 1):
            display_book(book, idx)
    else:
        print("No matching books found!")
