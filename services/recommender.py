# recommender.py

from services.embedding_service import embed_text
from utils.prompt_builder import build_prompt, build_combined_prompt
from services.rag_recommender import recommend_by_vector
from services.llm_service import generate_recommendation_text
from services.score_calculator import compute_final_scores

# ------------------------------
# 1. 설문 기반 추천
# ------------------------------
def recommend(user_input: dict):
    # 1. 사용자의 설문 응답 → 자연어 쿼리 생성
    prompt_for_rag = build_prompt(user_input)
    embedding = embed_text(prompt_for_rag)  # 쿼리를 벡터로 임베딩

    # 2. FAISS 유사도 반환
    similar_sounds = recommend_by_vector(embedding)

    # 3. LLM 추천 멘트를 위해 Top 3만 추림
    top_3_for_llm = similar_sounds[:3]

    # 사용자의 사운드 취향 정보 전달
    user_preferences = {
        "preferredSleepSound": user_input.get("preferredSleepSound"),
        "calmingSoundType": user_input.get("calmingSoundType")
    }

    # 4. LLM 호출로 추천 멘트 생성
    final_recommendation_text = ""
    try:
        final_recommendation_text = generate_recommendation_text(
            user_prompt=prompt_for_rag, 
            sound_results=top_3_for_llm,
            user_preferences=user_preferences
        )
    except Exception as e:
        # 실패 시 fallback 멘트 생성
        print(f"LLM generation failed: {e}. Falling back to default text.")
        sound_titles = similar_sounds[0]['filename'] if similar_sounds else "추천 사운드"
        fallback_text = (
            f"당신의 현재 상황을 고려하여 몇 가지 사운드를 찾아봤어요. "
            f"'{sound_titles}' 같은 소리는 어떠신가요? "
            f"오늘 밤, 이 소리들과 함께 편안한 시간을 보내시길 바래요."
        )
        final_recommendation_text = fallback_text
    
    # 5. 응답을 위해 rank, preference 필드 추가
    for i, sound_obj in enumerate(similar_sounds):
        sound_obj['rank'] = i + 1
        sound_obj['preference'] = 'none'

    # 6. 최종 응답 리턴
    return {
        "recommendation_text": final_recommendation_text,
        "recommended_sounds": similar_sounds
    }




# ------------------------------
# 3. 통합 추천 (수면 데이터 + 설문 데이터)
# ------------------------------
def recommend_with_both_data(user_input: dict):
    print("[recommend_with_both_data] user_input:", user_input)
    
    # 1. 수면 데이터와 설문 데이터를 모두 사용한 프롬프트 생성
    sleep_data = {
        "previous": user_input["previous"],
        "current": user_input["current"]
    }
    
    survey_data = {k: v for k, v in user_input.items() 
                   if k not in ["userId", "preferenceMode", "preferredSounds", 
                               "previous", "current", "previousRecommendations"]}
    
    prompt_for_rag = build_combined_prompt(sleep_data, survey_data)
    print("[recommend_with_both_data] prompt_for_rag:", prompt_for_rag)
    
    # 2. 통합 프롬프트로 임베딩 생성
    embedding = embed_text(prompt_for_rag["summary"])
    print("[recommend_with_both_data] embedding shape:", getattr(embedding, 'shape', None))
    
    # 3. FAISS 유사도 검색
    similar_sounds = recommend_by_vector(embedding)
    print(f"[recommend_with_both_data] similar_sounds (top 3): {[s.get('filename') for s in similar_sounds[:3]]}")
    
    # 4. 점수 계산 (수면 데이터 기반)
    scored = compute_final_scores(
        candidates=similar_sounds,
        preferred_ids=user_input["preferredSounds"],
        effectiveness_input={
            "prev_score": user_input["previous"]["sleepScore"],
            "curr_score": user_input["current"]["sleepScore"],
            "main_sounds": user_input["previousRecommendations"][:1],  
            "sub_sounds": user_input["previousRecommendations"][1:]    
        },
        mode=user_input["preferenceMode"],  # preference or effectiveness
        balance=user_input.get("preferenceBalance")  # 0.0~1.0 실수값
    )
    print(f"[recommend_with_both_data] scored (top 3): {[{'filename': s['sound'].get('filename'), 'score': s['score']} for s in scored[:3]]}")
    
    # 5. Top 3 추출
    top3 = [s["sound"] for s in scored[:3]]
    
    # 6. LLM으로 추천 텍스트 생성 (설문 데이터의 선호도 정보 포함)
    user_preferences = {
        "preferredSleepSound": user_input.get("preferredSleepSound"),
        "calmingSoundType": user_input.get("calmingSoundType"),
        "noisePreference": user_input.get("noisePreference")
    }
    
    text = generate_recommendation_text(
        user_prompt=prompt_for_rag,
        sound_results=top3,
        user_preferences=user_preferences
    )
    print("[recommend_with_both_data] LLM text:", text)
    
    # 7. 응답 형식 맞추기
    for i, s in enumerate(scored):
        s["sound"]["rank"] = i + 1
        s["sound"]["preference"] = (
            "top" if s["id"] in user_input["preferredSounds"] else "none"
        )
    
    return {
        "recommendation_text": text,
        "recommended_sounds": [s["sound"] for s in scored]
    }
