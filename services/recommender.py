# services/recommender.py
from services.embedding_service import embed_text
from utils.prompt_builder import build_prompt, build_sleep_prompt
from services.rag_recommender import recommend_by_vector
from services.llm_service import generate_recommendation_text
from services.score_calculator import compute_final_scores

def recommend(user_input: dict):
    # 1. RAG 검색용 쿼리 생성
    prompt_for_rag = build_prompt(user_input)
    embedding = embed_text(prompt_for_rag)

    # 2. FAISS를 통해 '유사도 순으로 정렬된 Top 5' 사운드 목록을 가져옴
    similar_sounds = recommend_by_vector(embedding) # top_k 기본값이 5이므로 5개가 옴

    # 3. LLM에게는 그 중에서도 가장 유사한 Top 3 정보만 전달
    top_3_for_llm = similar_sounds[:3]

    # 사용자가 선호하는 소리도 같이 넘겨주기
    user_preferences = {
        "preferredSleepSound": user_input.get("preferredSleepSound"),
        "calmingSoundType": user_input.get("calmingSoundType")
    }

    final_recommendation_text = "" # fallback을 대비해 미리 변수 선언
    try:
        final_recommendation_text = generate_recommendation_text(
            user_prompt=prompt_for_rag, 
            sound_results=top_3_for_llm,
            user_preferences=user_preferences
        )
    except Exception as e:
        print(f"LLM generation failed: {e}. Falling back to default text.")
        sound_titles = similar_sounds[0]['filename'] if similar_sounds else "추천 사운드"
        fallback_text = (
            f"당신의 현재 상황을 고려하여 몇 가지 사운드를 찾아봤어요. "
            f"'{sound_titles}' 같은 소리는 어떠신가요? "
            f"오늘 밤, 이 소리들과 함께 편안한 시간을 보내시길 바래요."
        )
        final_recommendation_text = fallback_text
    
    # 4. 프론트에 전달할 최종 목록 만들기
    # RAG가 찾아준 유사도 순서(similar_sounds) 그대로, rank와 preference 필드만 추가
    for i, sound_obj in enumerate(similar_sounds):
        sound_obj['rank'] = i + 1  # 랭킹은 1부터 시작
        sound_obj['preference'] = 'none'

    # 5. 최종 응답 구성
    response = {
        "recommendation_text": final_recommendation_text,
        "recommended_sounds": similar_sounds # rank와 preference가 추가된 5개 목록 전달
    }
    
    return response

def recommend_with_sleep_data(user_input: dict):
    # 1. 쿼리 생성 → 수면 상태 기반 자연어 쿼리
    prompt_for_rag = build_sleep_prompt(user_input["current"])

    # 2. 임베딩 + FAISS 검색
    embedding = embed_text(prompt_for_rag)
    similar_sounds = recommend_by_vector(embedding)

    # 3. 점수 계산
    scored = compute_final_scores(
        candidates=similar_sounds,
        preferred_ids=user_input["preferredSounds"],
        effectiveness_input={
            "prev_score": user_input["previous"]["sleepScore"],
            "curr_score": user_input["current"]["sleepScore"],
            "recommended": user_input["previousRecommendations"]
        },
        mode=user_input["preferenceMode"]
    )

    top3 = [s["sound"] for s in scored[:3]]

    # 4. LLM 추천문 생성
    text = generate_recommendation_text(
        user_prompt=prompt_for_rag,
        sound_results=top3,
        user_preferences={"preferredSleepSound": user_input.get("preferredSounds", [None])[0]}
    )

    # 5. 최종 응답 구성
    for i, (sound_obj, _) in enumerate(scored):
        sound_obj["rank"] = i + 1
        sound_obj["preference"] = "top" if sound_obj["id"] in user_input["preferredSounds"] else "none"

    return {
        "recommendation_text": text,
        "recommended_sounds": [s["sound"] for s in scored]
    }