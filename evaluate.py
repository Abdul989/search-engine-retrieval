import numpy as np
from search_books import search

def precision_at_k(relevant, retrieved, k):
    """
    Compute Precision@K: the fraction of the top K retrieved documents that are relevant.
    """
    retrieved_k = retrieved[:k]
    if not retrieved_k:
        return 0.0
    relevant_retrieved = [doc for doc in retrieved_k if doc in relevant]
    return len(relevant_retrieved) / len(retrieved_k)

def recall_at_k(relevant, retrieved, k):
    """
    Compute Recall@K: the fraction of all relevant documents that are retrieved in the top K.
    """
    retrieved_k = retrieved[:k]
    if not relevant:
        return 0.0
    relevant_retrieved = [doc for doc in retrieved_k if doc in relevant]
    return len(relevant_retrieved) / len(relevant)

def reciprocal_rank(relevant, retrieved):
    """
    Compute the Reciprocal Rank, defined as 1 divided by the rank position of the first relevant document.
    """
    for idx, doc in enumerate(retrieved, start=1):
        if doc in relevant:
            return 1.0 / idx
    return 0.0

def ndcg_at_k(relevant, retrieved, k):
    """
    Compute Normalized Discounted Cumulative Gain (NDCG) at K.
    We assume binary relevance: 1 if relevant, 0 otherwise.
    """
    dcg = 0.0
    for i, doc in enumerate(retrieved[:k]):
        rel = 1.0 if doc in relevant else 0.0
        dcg += (2**rel - 1) / np.log2(i + 2)  # +2 because i is zero-indexed

    # Ideal DCG (IDCG): assume all relevant documents are at the top positions
    ideal_rels = [1.0] * min(len(relevant), k)
    idcg = 0.0
    for i, rel in enumerate(ideal_rels):
        idcg += (2**rel - 1) / np.log2(i + 2)
    if idcg == 0:
        return 0.0
    return dcg / idcg

def evaluate_query(query, relevant_docs, k=10):
    """
    Executes a search query and computes evaluation metrics:
    Precision@K, Recall@K, Reciprocal Rank, and NDCG@K.
    
    :param query: The search query as a string.
    :param relevant_docs: A list of expected relevant document IDs (e.g., ISBNs).
    :param k: Number of top documents to consider.
    :return: A tuple (precision, recall, reciprocal rank, NDCG, retrieved_docs)
    """
    results = search(query, size=k)
    # Extract document IDs (assuming ISBN is used as document id in the index)
    retrieved_docs = [hit["_source"].get("ISBN") for hit in results["hits"]["hits"]]
    
    prec = precision_at_k(relevant_docs, retrieved_docs, k)
    rec = recall_at_k(relevant_docs, retrieved_docs, k)
    rr = reciprocal_rank(relevant_docs, retrieved_docs)
    ndcg = ndcg_at_k(relevant_docs, retrieved_docs, k)
    
    return prec, rec, rr, ndcg, retrieved_docs

def main():
    # Define sample queries and their expected relevant document ISBNs.
    # Adjust these sample queries and relevance judgments according to your data.
    sample_queries = {
        "flu pandemic 1918": ["0374157065"],
        "kitchen gods": ["0399135782"],
        "pirates": ["0679425608"],
        "pride and prejudice": ["055321215X"],
        "beloved": ["0440234743"]
    }
    
    k = 10  # evaluate metrics for top-10 results
    all_prec, all_rec, all_rr, all_ndcg = [], [], [], []
    
    print("Evaluation Results:\n" + "-" * 40)
    for query, relevant in sample_queries.items():
        prec, rec, rr, ndcg, retrieved = evaluate_query(query, relevant, k)
        print(f"\nQuery: '{query}'")
        print(f"Expected Relevant ISBNs: {relevant}")
        print(f"Retrieved ISBNs: {retrieved}")
        print(f"Precision@{k}: {prec:.2f}")
        print(f"Recall@{k}: {rec:.2f}")
        print(f"Reciprocal Rank: {rr:.2f}")
        print(f"NDCG@{k}: {ndcg:.2f}")
        all_prec.append(prec)
        all_rec.append(rec)
        all_rr.append(rr)
        all_ndcg.append(ndcg)
    
    print("\nOverall Evaluation Metrics:")
    print(f"Mean Precision@{k}: {np.mean(all_prec):.2f}")
    print(f"Mean Recall@{k}: {np.mean(all_rec):.2f}")
    print(f"Mean Reciprocal Rank (MRR): {np.mean(all_rr):.2f}")
    print(f"Mean NDCG@{k}: {np.mean(all_ndcg):.2f}")

if __name__ == "__main__":
    main()