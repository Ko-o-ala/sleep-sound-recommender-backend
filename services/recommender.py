from services.embedding_service import embed_text
from utils.prompt_builder import build_prompt
from services.rag_recommender import recommend_by_vector
from services.llm_service import generate_recommendation_text

def recommend(user_input: dict):
    # 사용자 입력을 자연어 쿼리로 변환
    prompt_for_rag = build_prompt(user_input)

    # 쿼리를 임베딩 벡터로 변환
    embedding = embed_text(prompt_for_rag)

    # RAG로 유사한 사운드 검색
    simliar_sounds = recommend_by_vector(embedding)

    # LLM 호출 + fallback 로직
    try:
        print("Attempting to generate recommendation from LLM...")
        final_recommendation_text = generate_recommendation_text(
        user_prompt=prompt_for_rag,
        sound_results=simliar_sounds
    )
    except Exception as e:
        # LLM 호출 중 에러 발생하는 경우
        print(f"LLM generation failed: {e}. Falling back to default text.")
        sound_titles = ", ".join([sound['filename'] for sound in similar_sounds])
        fallback_text = (
            f"당신의 현재 상황을 고려하여 몇 가지 사운드를 찾아봤어요. "
            f"'{sound_titles}' 같은 소리는 어떠신가요? "
            f"오늘 밤, 이 소리들과 함께 편안한 시간을 보내시길 바래요."
        )
        final_recommendation_text = fallback_text

    # 최종 결과물을 조합해서 리턴
    response = {
        "recommendation_text": final_recommendation_text,
        "recommended_sounds": [sound["filename"] for sound in simliar_sounds]
    }
    return response