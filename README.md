# Book Search Engine

This project is an information retrieval (IR) system that indexes a collection of books and enables keyword-based search with enhanced ranking using Elasticsearch and BM25. It also supports evaluation of retrieval performance and offers an interactive UI via Streamlit.

## Project Overview

The Book Search Engine project implements:
- **Indexing:**  
  Preprocessing and indexing of book data from a JSON file into Elasticsearch using BM25 similarity with configurable parameters and field-specific boosts.
  
- **Search:**  
  A search functionality (in `search_books.py`) that queries multiple fields with BM25 ranking and applies an additional boost based on the document's average rating.
  
- **Evaluation:**  
  An evaluation script (`evaluate.py`) that computes metrics such as Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and Normalized Discounted Cumulative Gain (NDCG) to assess the retrieval effectiveness.
  
- **Interactive UI:**  
  A Streamlit-based dashboard (`app.py`) that provides an integrated user interface for re-indexing, searching (with pagination and clickable details), and evaluation.

## Features

- **BM25-Based Ranking:**  
  Searches across Title, Author, Publisher, Description, and Search_Text with boosts on Title and Author to highlight their importance.
  
- **Rating Boost:**  
  Applies an additional boost based on Average_Rating using a field value factor.
  
- **Pagination & Expandable Results:**  
  Shows 20 results per page; each result is clickable (via an expander) to reveal details such as Author, Publisher, Timestamp, Rating, Description, and Format.
  
- **Evaluation Metrics:**  
  Computes evaluation metrics to measure the relevance and ranking performance of the search engine.

## Requirements

The project requires Python 3 and the following packages:

- numpy
- elasticsearch==7.16.0
- streamlit

All dependencies are listed in the [`requirements.txt`](requirements.txt) file.

## Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>

2. **Setup venv:**
   ```bash
    python3 -m venv venv
    source venv/bin/activate

3. **Install Dependencies:**
   ```bash
    pip install -r requirements.txt

4. **Run UI**
   ```
   streamlit run app.py
