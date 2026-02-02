import json
import re
import requests
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi


txtpath=r"C:\Users\gangeshvar.s\Downloads\hair_buzz_lease_ocrtext (1).txt"

with open(txtpath,'r') as f:
    content=json.load(f)

configpath=r"C:\Users\gangeshvar.s\Desktop\chunks\config.json"

with open(configpath,'r') as p:
    config=json.load(p)

device = config['device']
CHUNK_SIZE = config['CHUNK_SIZE']
CHUNK_OVERLAP = config['CHUNK_OVERLAP']
MIN_CHUNK_SIZE = config['MIN_CHUNK_SIZE']

HNSW_M = config['HNSW_M']
HNSW_EF_CONSTRUCTION = config['HNSW_EF_CONSTRUCTION']
HNSW_EF_SEARCH = config['HNSW_EF_SEARCH']   
EMBED_DIM = config['EMBED_DIM']

embed_model_name = config["EMBED_MODEL"]
rerank_model_name = config["RERANK_MODEL"]

# Load model on CPU
model = SentenceTransformer(
    embed_model_name,
    device=device
)


reranker = CrossEncoder(
    rerank_model_name,
    device=device
)

query="What is the landlord's name?"


def chunking(pages):
    all_chunks = []

    for i,p in enumerate(pages,start=1):
        words = p['text'].split()
        start = 0
        page_chunks_added = 0  # track valid chunks for this page
        
        while start < len(words):
            end = start + CHUNK_SIZE
            chunk = words[start:end]
        
            if len(chunk) >= MIN_CHUNK_SIZE:
                all_chunks.append({"page": i , "chunk": " ".join(chunk)})
                page_chunks_added += 1
        
            start += CHUNK_SIZE - CHUNK_OVERLAP

        # fallback: add entire page if no valid chunk was added
        if page_chunks_added == 0 and len(words) > 0:
            all_chunks.append({
                "page": i,
                "chunk": p["text"]
            })
        
    print(f"Total no of chunks : {len(all_chunks)}")
    return all_chunks


def embed_texts(texts):
    
    embeddings = model.encode(
    texts,
    batch_size=16,              # smaller batch works better on CPU
    normalize_embeddings=True,
    convert_to_numpy=True
    )

    # Keep float32 for CPU
    embeddings = embeddings.astype(np.float32)

    index = faiss.IndexHNSWFlat(EMBED_DIM, HNSW_M)
    index.hnsw.efConstruction = HNSW_EF_CONSTRUCTION
    index.hnsw.efSearch = HNSW_EF_SEARCH
    index.add(embeddings)
    return index

def build_bm25(texts):
    tex = [
    re.sub(r"[^a-z0-9\s]", " ", i.lower())
    for i in texts
    ]
    tokenized = [c.split() for c in tex]
    bm25=BM25Okapi(tokenized)
    return bm25

def sparse_retrieval(bm25,query,retchunksby2):
    sparse_scores = bm25.get_scores(query.split())
    sparse_ids = np.argsort(sparse_scores)[-retchunksby2:]
    return sparse_ids
    

def query_embed(query):
    q_emb = model.encode(
    query,
    batch_size=16,              # smaller batch works better on CPU
    normalize_embeddings=True,
    convert_to_numpy=True
    )

    # Keep float32 for CPU
    q_emb = q_emb.astype(np.float32)
    q_emb = q_emb.reshape(1, -1)
    return q_emb


def dense_retrieval(index, q_emb, retchunksby2):
    _, ids = index.search(q_emb, k=retchunksby2)
    dense_ids=ids[0]
    return dense_ids


def reranking(candidates):
    pairs = [(query, d) for d in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return ranked
    

def main(content):
    
    t=content['texts']

    pages=[]
    
    for k,v in t.items():
        pages.append({"page": int(k), "text": v}) 

    sorted_data = sorted(pages, key=lambda x: x["page"])
    print(f"Number of pages in the document:{len(sorted_data)}")
    chunks=chunking(sorted_data)
    
    retchunks=int(0.2*len(chunks))
    retchunksby2=int(retchunks/2)
    
    texts=[c['chunk'] for c in chunks]
    metadatas=[c['page'] for c in chunks]

    id_to_metadata = { i: metadatas[i] for i in range(len(metadatas)) } 
    id_to_text = { i: texts[i] for i in range(len(texts)) }

    bm25 = build_bm25(texts)

    sparse_ids = sparse_retrieval(bm25,query,retchunksby2)
    print(f"Sparse top {retchunksby2} ids:{sparse_ids}")

    index = embed_texts(texts)
    
    q_emb = query_embed(query)

    dense_ids = dense_retrieval(index, q_emb, retchunksby2)

    candidate_ids = set(dense_ids) | set(sparse_ids)

    candidates = [
    f"Page {id_to_metadata[i]}: {id_to_text[i]}"
    for i in candidate_ids
    ]

    print(f"Total candidate chunks for reranking: {len(candidates)}")

    ranked = reranking(candidates)
    
    top_k=10
    reranked = [d for d, _ in ranked[:top_k]]
    
    with open(r"C:\Users\gangeshvar.s\Desktop\chunks\1stquery",'w') as f:
        for chunk in reranked:
            f.write(chunk)
            f.write("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main(content)







