import faiss
import numpy as np
import json

faiss_index = faiss.read_index("data/sound_index.faiss")
with open("data/sound_pool.json", "r") as f:
    sound_pool = json.load(f)

def recommend_by_vector(query_vector: np.ndarray, top_k: int = 5):
    D, I = faiss_index.search(np.array([query_vector]), top_k)
    results = [sound_pool[i] for i in I[0]]

    # 디버깅용 추가
    """
    print("--- RAG 검색 결과 (results) ---")
    print(results)
    print("--- 결과의 타입 (type) ---")
    print(type(results))
    print("--- 첫 번째 항목의 타입 (type) ---")
    if results:
        print(type(results[0]))
    print("----------------------------")
    """

    return results