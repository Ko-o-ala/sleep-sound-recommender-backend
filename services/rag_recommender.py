# rag_recommender.py
# RAG에서 Retrieve를 담당하는 부분

import faiss
import numpy as np
import json

# 미리 만들어둔 FAISS 인덱스, 원본 사운드 데이터 로드
faiss_index = faiss.read_index("data/sound_index.faiss")
with open("data/sound_pool.json", "r") as f:
    sound_pool = json.load(f)

# 유사도 검색 -> 유사도 높은 순으로 정렬된 사운드 리스트 리턴
def recommend_by_vector(query_vector: np.ndarray, top_k: int = 22):
    D, I = faiss_index.search(np.array([query_vector]), top_k)
    results = [sound_pool[i] for i in I[0]]

    return results