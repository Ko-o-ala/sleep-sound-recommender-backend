import faiss
import numpy as np
import json

def build_faiss_index(embedding_path: str, index_path: str):
    with open(embedding_path, 'r') as f:
        embeddings = json.load(f)

    vectors = np.array([v["embedding"] for v in embeddings], dtype='float32')
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, index_path)
    print(f"FAISS index saved to {index_path}")

if __name__ == "__main__":
    build_faiss_index(
        "data/sound_pool_embedding.json",
        "data/sound_index.faiss"
    )