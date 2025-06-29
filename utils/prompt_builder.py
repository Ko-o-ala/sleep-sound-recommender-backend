# utils/prompt_builder.py
from typing import Dict, List, Optional
from services.llm_service import translate_korean_to_english

def build_prompt(user_survey: Dict[str, any]) -> str:
    """
    상세한 설문조사 딕셔너리를 바탕으로,
    한글이 포함된 필드는 영어로 번역하여,
    임베딩 모델이 이해하기 좋은 순수 영어 문장(쿼리)을 생성한다.
    """
    phrases = []

    # --- 1. 번역이 필요한 필드들 먼저 처리 ---
    # ▼▼▼ .get(...) or "" 를 사용해서, 값이 None일 경우에도 안전하게 빈 문자열로 처리! ▼▼▼
    noise_other = user_survey.get("noisePreferenceOther") or ""
    youtube_other = user_survey.get("youtubeContentTypeOther") or ""
    
    # 번역 실행!
    translated_noise_other = translate_korean_to_english(noise_other)
    translated_youtube_other = translate_korean_to_english(youtube_other)

    # --- 2. 모든 정보를 조합하여 최종 쿼리 생성 (이하 동일) ---
    if goal := user_survey.get("sleepGoal"):
        phrases.append(f"wants to achieve the goal of '{goal}'")
    if issues := user_survey.get("sleepIssues"):
        phrases.append(f"is experiencing sleep issues like '{', '.join(issues)}'")
    if stress := user_survey.get("stressLevel"):
        phrases.append(f"and has a '{stress}' stress level.")

    if sound_pref := user_survey.get("preferredSleepSound"):
        phrases.append(f"They generally prefer '{sound_pref}' sounds.")
    
    if translated_noise_other:
        phrases.append(f"and also likes '{translated_noise_other}'.")
    if translated_youtube_other:
        phrases.append(f"They also watch '{translated_youtube_other}' on YouTube.")

    if not phrases:
        return "A user seeking better sleep."

    final_prompt = "A user who " + " ".join(phrases)
    print(f"DEBUG: Generated RAG Query: {final_prompt}")
    return final_prompt