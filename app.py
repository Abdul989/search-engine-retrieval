import sys
import subprocess
import streamlit as st
from pathlib import Path
from elasticsearch import Elasticsearch

# Set boost mode for the search query (options: "sum", "multiply", "max", etc.)
BOOST_MODE = "multiply"

def search_paginated(query, index="books_index", size=20, page=1):
    """
    Performs a paginated search using a function_score query.
    It uses a multi_match query across several fields and combines the BM25 score
    with a field_value_factor on Average_Rating. The 'from' parameter is computed
    based on the page number.
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
                    "modifier": "sqrt",  # Moderate the influence of rating
                    "missing": 1         # Default if field is missing
                },
                "boost_mode": BOOST_MODE
            }
        },
        "size": size,
        "from": from_value
    }
    
    return es.search(index=index, body=body)

# Resolve project directory once
PROJECT_DIR = Path(__file__).resolve().parent

st.title("Book Search Engine Dashboard")

# Sidebar: Select the action to perform
st.sidebar.header("Actions")
action = st.sidebar.selectbox("Select an action", ["Search", "Re-index Data", "Evaluation"])

if action == "Re-index Data":
    st.header("Re-indexing Data")
    st.write("Starting data indexing. This may take a moment…")

    index_script = PROJECT_DIR / "index_books.py"
    books_file   = PROJECT_DIR / "books.json"

    # Run the indexing script with the same Python interpreter
    result = subprocess.run(
        [sys.executable, str(index_script), str(books_file)],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True
    )

    # Display raw output without stderr section
    st.code(result.stdout or "— no stdout —", language="bash")

    if result.returncode == 0:
        st.success("Indexing complete!")
    else:
        # Display just one error area
        st.text_area("Error Details", result.stderr or "— no stderr —", height=200)
        st.error("Indexing failed. See the error details above.")

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
                src = hit["_source"]
                score = hit.get("_score", 0)
                with st.expander(f"{src.get('Title','N/A')} (Score: {score:.2f})"):
                    st.markdown(f"**Author:** {src.get('Author','N/A')}")
                    st.markdown(f"**Publisher:** {src.get('Publisher','N/A')}")
                    st.markdown(f"**Timestamp:** {src.get('timestamp','N/A')}")
                    st.markdown(f"**Rating:** {src.get('Average_Rating','N/A')}")
                    st.markdown(f"**Description:** {src.get('Description','N/A')}")
                    st.markdown(f"**Format:** {src.get('Format','N/A')}")
        else:
            st.warning("No results found for your query.")

elif action == "Evaluation":
    st.header("Evaluation Results")
    eval_script = PROJECT_DIR / "evaluate.py"
    with st.spinner("Running evaluation..."):
        result = subprocess.run(
            [sys.executable, str(eval_script)],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True
        )

    # Display only stdout for evaluation
    st.text_area("", result.stdout, height=200)

    if result.returncode == 0:
        st.success("Evaluation complete!")
    else:
        st.error("Evaluation encountered an error.")

