import faiss
import numpy as np
import json
from embed_generator import generate_embedding

def build_faiss_index(sound_pool_path: str, index_path: str):
    # 원본 데이터 로드
    print(f"Loading sound data from {sound_pool_path}...")
    with open(sound_pool_path, 'r', encoding='utf-8') as f:
        sound_pool = json.load(f)

    # 각 사운드의 effect를 임베딩 벡터로 변환
    print("Generating embeddings for each sound...")
    embeddings = [generate_embedding(item['effect']) for item in sound_pool]
    vectors = np.array(embeddings, dtype='float32')

    # FAISS 인덱스 생성 및 저장
    print("Building FAISS index...")
    index = faiss.IndexFlatL2(vectors.shape[1]) # 384차원, l2 거리 기반 인덱스
    index.add(vectors)
    faiss.write_index(index, index_path)
    print(f"FAISS index with {len(vectors)} vectors saved to {index_path}")

if __name__ == "__main__":
    build_faiss_index(
        "data/sound_pool.json",     # 여기서 원본 데이터 읽음
        "data/sound_index.faiss"    # 여기다가 결과물 저장
    )