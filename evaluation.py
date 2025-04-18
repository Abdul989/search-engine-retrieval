import numpy as np
from query_search import search_books
import re

def normalize(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    return text.strip()

def is_relevant(doc, relevant_phrases):
    title = normalize(doc.get("Title", ""))
    publisher = normalize(doc.get("Publisher", ""))
    desc = normalize(doc.get("Desc", ""))
    return any(phrase in title or phrase in publisher or phrase in desc for phrase in relevant_phrases)

def precision_at_k(relevant_docs, retrieved_docs, k):
    retrieved_k = retrieved_docs[:k]
    if not retrieved_k:
        return 0.0
    relevant_retrieved = [doc for doc in retrieved_k if doc["is_relevant"]]
    return len(relevant_retrieved) / len(retrieved_k)

def recall_at_k(relevant_docs, retrieved_docs, k):
    if not relevant_docs:
        return 0.0
    relevant_retrieved = [doc for doc in retrieved_docs[:k] if doc["is_relevant"]]
    return len(relevant_retrieved) / len(relevant_docs)

def reciprocal_rank(retrieved_docs):
    for idx, doc in enumerate(retrieved_docs, start=1):
        if doc["is_relevant"]:
            return 1.0 / idx
    return 0.0

def ndcg_at_k(retrieved_docs, k):
    dcg = 0.0
    for i, doc in enumerate(retrieved_docs[:k]):
        rel = 1.0 if doc["is_relevant"] else 0.0
        dcg += (2**rel - 1) / np.log2(i + 2)
    
    ideal_rels = sorted([1.0]*sum(doc["is_relevant"] for doc in retrieved_docs[:k]), reverse=True)
    idcg = sum((2**rel - 1) / np.log2(i + 2) for i, rel in enumerate(ideal_rels))
    return dcg / idcg if idcg != 0 else 0.0

def evaluate_query(query, relevant_phrases, k=10):
    relevant_phrases = [normalize(p) for p in relevant_phrases]
    retrieved_docs = search_books(query, size=k)
    
    for doc in retrieved_docs:
        doc["is_relevant"] = is_relevant(doc, relevant_phrases)

    relevant_docs = [doc for doc in retrieved_docs if doc["is_relevant"]]

    prec = precision_at_k(relevant_docs, retrieved_docs, k)
    rec = recall_at_k(relevant_docs, retrieved_docs, k)
    rr = reciprocal_rank(retrieved_docs)
    ndcg = ndcg_at_k(retrieved_docs, k)
    
    return prec, rec, rr, ndcg, retrieved_docs

def main():
    sample_queries = {
        "flu pandemic 1918": ["the great influenza"],
        "kitchen gods": ["the kitchen god's wife"],
        "pirates": ["pirates!"],
        "pride and prejudice": ["pride and prejudice"],
        "beloved": ["beloved"],
        "harry": ["harry"],
        "harry potter": ["harry potter"],
        "random house": ["random house"]
    }

    k = 15
    all_prec, all_rec, all_rr, all_ndcg = [], [], [], []

    print("Evaluation Results:\n" + "-" * 40)
    for query, relevant_phrases in sample_queries.items():
        prec, rec, rr, ndcg, retrieved = evaluate_query(query, relevant_phrases, k)
        
        print(f"\nQuery: '{query}'")
        print(f"Relevant Phrases: {relevant_phrases}")
        print(f"Top-{k} Retrieved Titles:")
        for i, book in enumerate(retrieved[:k], 1):
            rel_marker = "1" if book["is_relevant"] else "0"
            print(f"{i}. {book.get('Title', 'N/A')} (ISBN: {book.get('ISBN', 'N/A')}) {rel_marker}")

        print(f"\nPrecision@{k}: {prec:.2f}")
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
