import streamlit as st
import subprocess
from elasticsearch import Elasticsearch

# Set boost mode for the search query (options: "sum", "multiply", "max", etc.)
BOOST_MODE = "multiply"

def search_paginated(query, index="books_index", size=20, page=1):
    """
    Performs a paginated search using a function_score query.
    It uses a multi_match query across several fields and combines the BM25 score with a field value
    factor on Average_Rating. The 'from' parameter is computed based on the page number.
    """
    es = Elasticsearch("http://localhost:9200")
    from_value = (page - 1) * size

    body = {
        "query": {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "Title^2",       # Boost the Title field
                            "Author^1.5",    # Boost the Author field
                            "Publisher",
                            "Description",
                            "Search_Text"
                        ]
                    }
                },
                "field_value_factor": {
                    "field": "Average_Rating",
                    "factor": 0.1,
                    "modifier": "sqrt",  # Use square-root to moderate the influence of rating
                    "missing": 1         # Default value if the field is missing
                },
                "boost_mode": BOOST_MODE  # Combine the BM25 score and the rating boost as per BOOST_MODE
            }
        },
        "size": size,
        "from": from_value
    }
    
    res = es.search(index=index, body=body)
    return res

st.title("Book Search Engine Dashboard")

# Sidebar: Select the action to perform
st.sidebar.header("Actions")
action = st.sidebar.selectbox("Select an action", ["Search", "Re-index Data", "Evaluation"])

if action == "Re-index Data":
    st.header("Re-indexing Data")
    st.write("Starting data indexing. This may take a moment...")
    # Run the indexing script (assuming index_books.py is in the same directory)
    result = subprocess.run(["python3", "index_books.py", "books.json"], capture_output=True, text=True)
    st.code(result.stdout)
    if result.returncode == 0:
        st.success("Indexing complete!")
    else:
        st.error("Indexing encountered an error. Check the logs for details.")

elif action == "Search":
    st.header("Search the Book Index")
    query = st.text_input("Enter your search query:")
    
    # Pagination: 20 results per page
    results_per_page = 20
    page = st.number_input("Page Number", min_value=1, value=1, step=1)
    
    if query:
        with st.spinner("Searching..."):
            results = search_paginated(query, size=results_per_page, page=page)
        total_hits = results.get("hits", {}).get("total", {}).get("value", 0)
        st.write(f"Total matching documents: {total_hits}")
        
        hits = results.get("hits", {}).get("hits", [])
        if hits:
            st.subheader("Search Results")
            for hit in hits:
                source = hit["_source"]
                title       = source.get("Title", "N/A")
                author      = source.get("Author", "N/A")
                publisher   = source.get("Publisher", "N/A")
                timestamp   = source.get("timestamp", "N/A")
                rating      = source.get("Average_Rating", "N/A")
                description = source.get("Description", "N/A")
                book_format = source.get("Format", "N/A")
                score       = hit.get("_score", 0)
                
                # Create an expander widget with the clickable title (including the Score)
                with st.expander(f"{title} (Score: {score:.2f})"):
                    st.markdown(f"**Author:** {author}")
                    st.markdown(f"**Publisher:** {publisher}")
                    st.markdown(f"**Timestamp:** {timestamp}")
                    st.markdown(f"**Rating:** {rating}")
                    st.markdown(f"**Description:** {description}")
                    st.markdown(f"**Format:** {book_format}")
        else:
            st.warning("No results found for your query.")

elif action == "Evaluation":
    st.header("Evaluation Results")
    with st.spinner("Running evaluation..."):
        result = subprocess.run(["python3", "evaluate.py"], capture_output=True, text=True)
    st.text_area("Evaluation Output", result.stdout, height=400)
    if result.returncode != 0:
        st.error("Evaluation encountered an error. Check the logs for details.")
    else:
        st.success("Evaluation complete!")