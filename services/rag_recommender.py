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
    # 전체 사운드가 22개이므로 22개 검색
    D, I = faiss_index.search(np.array([query_vector]), top_k)
    
    # 유사도 점수를 포함하여 결과 생성
    results = []
    for i, (distance, index) in enumerate(zip(D[0], I[0])):
        sound = sound_pool[index].copy()
        # 거리를 유사도 점수로 변환 (0~1 범위)
        similarity_score = 1.0 / (1.0 + distance)
        sound['similarity_score'] = similarity_score
        results.append(sound)
    
    # 다양성을 위한 카테고리별 샘플링 (간단한 버전)
    diverse_results = []
    categories = {}
    
    # 카테고리별로 그룹화
    for sound in results:
        category = sound.get('category', '기타')
        if category not in categories:
            categories[category] = []
        categories[category].append(sound)
    
    # 각 카테고리에서 상위 2개씩 선택 (더 적게)
    for category, sounds in categories.items():
        top_sounds = sorted(sounds, key=lambda x: x['similarity_score'], reverse=True)[:2]
        diverse_results.extend(top_sounds)
    
    # 유사도 점수로 재정렬
    diverse_results = sorted(diverse_results, key=lambda x: x['similarity_score'], reverse=True)
    
    # 최종적으로 top_k개 반환
    return diverse_results[:top_k]