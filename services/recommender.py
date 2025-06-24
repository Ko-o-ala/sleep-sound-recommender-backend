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
    similar_sounds = recommend_by_vector(embedding)

    top_3_for_llm = similar_sounds[:3]

    try:
        # 이제 5개가 아닌, 3개 목록만 LLM에게 전달!
        final_recommendation_text = generate_recommendation_text(
            user_prompt=prompt_for_rag, 
            sound_results=top_3_for_llm # <-- top_3_for_llm 변수 사용
        )
    except Exception as e:
        print(f"LLM generation failed: {e}. Falling back to default text.")
        
        # fallback 로직에서도 가장 유사한 사운드 1개의 이름만 보여주도록 수정
        sound_titles = similar_sounds[0]['filename'] if similar_sounds else "추천 사운드"
        
        fallback_text = (
            f"당신의 현재 상황을 고려하여 몇 가지 사운드를 찾아봤어요. "
            f"'{sound_titles}' 같은 소리는 어떠신가요? "
            f"오늘 밤, 이 소리들과 함께 편안한 시간을 보내시길 바래요."
        )
        final_recommendation_text = fallback_text

    # ▼▼▼ 3. [변경점 2] 프론트엔드에는 전체 목록(5개)을 전달! ▼▼▼
    # recommended_sounds에 파일명 리스트 대신, 사운드 객체 리스트 전체를 담아준다.
    response = {
        "recommendation_text": final_recommendation_text,
        "recommended_sounds": similar_sounds # <-- 5개 전체 목록을 그대로 전달!
    }
    
    return response