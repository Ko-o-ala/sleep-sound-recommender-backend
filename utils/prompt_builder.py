from typing import Dict, List, Optional
from services.llm_service import translate_korean_to_english

def build_prompt(user_survey: Dict[str, any]) -> str:
    """
    설문조사 응답을 바탕으로 LLM에 전달할 영어 문장을 생성하는 함수.
    한글이 포함된 응답은 번역 후 자연어 형태로 연결함.
    """
    phrases = []

    # 1. 한글이 포함될 수 있는 기타 항목 추출 (값이 없을 경우 빈 문자열로 대체함)
    noise_other = user_survey.get("noisePreferenceOther") or ""
    youtube_other = user_survey.get("youtubeContentTypeOther") or ""

    # 2. 번역 수행 (한글 -> 영어)
    translated_noise_other = translate_korean_to_english(noise_other)
    translated_youtube_other = translate_korean_to_english(youtube_other)

    # 3. 주요 필드를 문장으로 조립
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

    # 4. 아무 정보도 없을 경우 fallback 문장
    if not phrases:
        return "A user seeking better sleep."

    # 5. 모든 문장을 하나의 문장으로 연결
    final_prompt = "A user who " + " ".join(phrases)
    print(f"DEBUG: Generated RAG Query: {final_prompt}")
    return final_prompt


def build_sleep_prompt(sleep_data: Dict) -> str:
    """
    수면 데이터를 기반으로 사용자의 상태를 요약하는 자연어 문장을 생성함.
    기준 이하의 deep/REM 수면, 과도한 깨어있음, 낮은 수면 점수를 체크하여 문장화함.
    """
    # 1. 수면 비율 계산
    deep = sleep_data.get("deepSleepDuration", 0)
    rem = sleep_data.get("remSleepDuration", 0)
    total = sleep_data.get("totalSleepDuration", 1)  
    awake = sleep_data.get("awakeDuration", 0)

    deep_ratio = deep / total
    rem_ratio = rem / total
    awake_ratio = awake / total
    score = sleep_data.get("sleepScore", 0)

    # 2. 상태 평가 조건에 따라 요약 문장 구성
    summary = []
    if deep_ratio < 0.15:
        summary.append("The user had insufficient deep sleep.")
    if rem_ratio < 0.2:
        summary.append("REM sleep ratio was too low.")
    if awake_ratio > 0.15:
        summary.append("The user experienced frequent awakenings.")
    if score < 70:
        summary.append("Overall sleep quality was poor based on the score.")

    # 3. 이상 없을 경우 기본 문장
    return " ".join(summary) or "Overall sleep quality was within a healthy range."
