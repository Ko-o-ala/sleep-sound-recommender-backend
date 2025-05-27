from services.embedding_service import embed_text
from utils.prompt_builder import build_prompt
from services.rag_recommender import recommend_by_vector

def recommend(user_input: dict):
    prompt = build_prompt(user_input)
    embedding = embed_text(prompt)
    results = recommend_by_vector(embedding)
    return results