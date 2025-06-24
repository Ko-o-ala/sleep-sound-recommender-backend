from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("BAAI/bge-large-en-v1.5")

def generate_embedding(text: str) -> np.ndarray:
    """
    주어진 입력(자연어)를 384차원의 임베딩 벡터로 변환

    Args:
        text (str): 임베딩할 텍스트
    
    Returns:
        np.ndarray: float32 타입 384차원 벡터
    """
    return model.encode(text).astype("float32")