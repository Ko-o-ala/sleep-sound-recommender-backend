import faiss
import numpy as np
import json

faiss_index = faiss.read_index("data/sound_index.faiss")
with open("data/sound_pool.json", "r") as f:
    sound_pool = json.load(f)

def recommend_by_vector(query_vector: np.ndarray, top_k: int = 5):
    D, I = faiss_index.search(np.array([query_vector]), top_k)
    results = [sound_pool[i] for i in I[0]]
    return results