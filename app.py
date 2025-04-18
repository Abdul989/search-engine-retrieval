import streamlit as st
import subprocess
from query_search import search_books  

st.title("Book Search Engine Dashboard")

# Sidebar for actions
st.sidebar.header("Actions")
action = st.sidebar.selectbox("Select an action", ["Search", "Re-index Data", "Evaluation"])

if action == "Re-index Data":
    st.header("Re-indexing Data")
    st.write("Starting data indexing. This may take a moment...")
    result = subprocess.run(["python3", "index_books.py", "books.json"], capture_output=True, text=True)
    st.code(result.stdout)
    if result.returncode == 0:
        st.success("Indexing complete!")
    else:
        st.error("Indexing encountered an error. Check the logs for details.")

elif action == "Search":
    st.header("Search the Book Index")
    query = st.text_input("Enter your search query:")

    if query:
        with st.spinner("Searching..."):
            results = search_books(user_query=query)

        if results:
            # Show total number of results
            total_results = len(results)
            st.success(f"{total_results} results found for '{query}'")

            results_per_page = 20
            total_pages = (total_results - 1) // results_per_page + 1

            # Initialize session state for pagination
            if "page" not in st.session_state:
                st.session_state.page = 1

            # Reset to page 1 if new search query
            if "last_query" not in st.session_state or st.session_state.last_query != query:
                st.session_state.page = 1
                st.session_state.last_query = query

            # Navigation buttons
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("⬅️ Prev") and st.session_state.page > 1:
                    st.session_state.page -= 1
            with col3:
                if st.button("Next ➡️") and st.session_state.page < total_pages:
                    st.session_state.page += 1

            # Set current page
            page = st.session_state.page
            start_idx = (page - 1) * results_per_page
            end_idx = min(start_idx + results_per_page, total_results)

            st.markdown(f"### Showing results {start_idx + 1} to {end_idx} of {total_results} (Page {page}/{total_pages})")

            for idx, book in enumerate(results[start_idx:end_idx], start=start_idx + 1):
                title       = book.get("Title", "N/A")
                author      = book.get("Author", "N/A")
                publisher   = book.get("Publisher", "N/A")
                timestamp   = book.get("timestamp", "N/A")
                rating      = book.get("Average_Rating", "N/A")
                description = book.get("Description", "N/A")
                book_format = book.get("Format", "N/A")

                with st.expander(f"{idx}. {title}"):
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
        result = subprocess.run(["python3", "evaluation.py"], capture_output=True, text=True)
    st.text_area("Evaluation Output", result.stdout, height=400)
    if result.returncode != 0:
        st.error("Evaluation encountered an error. Check the logs for details.")
    else:
        st.success("Evaluation complete!")
