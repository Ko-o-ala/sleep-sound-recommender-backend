# embed_generator.py

from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("BAAI/bge-large-en-v1.5")

# 주어진 입력(자연어)를 384차원의 임베딩 벡터로 변환
def generate_embedding(text: str) -> np.ndarray:
    try:
        # float32타입 382차원 벡터를 리턴
        return model.encode(text).astype("float32")
    
    # 예외처리
    except Exception as e:
        print(f"[ERROR] 임베딩 생성 실패: {e}")
        return np.zeros(384, dtype="float32")  # fallback