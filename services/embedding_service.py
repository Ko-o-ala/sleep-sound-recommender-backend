# embedding_service.py

import numpy as np
from scripts.embed_generator import generate_embedding

def embed_text(text: str) -> np.ndarray:
    """
    실제 SentenceTransformer 모델을 사용하여 입력 문장을 임베딩 벡터로 변환

    Args:
        text (str): 사용자로부터 입력받은 문장

    Returns:
        np.ndarray: 384차원의 float32 벡터
    """
    return generate_embedding(text)