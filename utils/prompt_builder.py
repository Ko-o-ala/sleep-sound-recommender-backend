# prompt_builder.py

from typing import Dict, List, Optional
from services.llm_service import translate_korean_to_english

# 설문 응답 데이터를 자연어 영어 문장으로 바꿔서 LLM에게 넘겨줄 프롬프트 생성
def build_prompt(user_survey: Dict[str, any]) -> str:
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

# 상태 평가해서 프롬프트에 추가해주는 함수
def evaluate_status(metric: float, thresholds: Dict[str, float]) -> str:
    if metric >= thresholds["good"]:
        return "good"
    elif metric >= thresholds["warning"]:
        return "warning"
    else:
        return "bad"

# 이전/현재의 수면 비율 데이터를 비교해 문장으로 수면 상태를 요약
def build_sleep_prompt(previous: Dict, current: Dict) -> Dict:
    print("[build_sleep_prompt] previous:", previous)
    print("[build_sleep_prompt] current:", current)
    summary = []

    # 변화량 계산
    deep_delta = round(current.get("deepSleepRatio", 0) - previous.get("deepSleepRatio", 0), 4)
    rem_delta = round(current.get("remSleepRatio", 0) - previous.get("remSleepRatio", 0), 4)
    awake_delta = round(current.get("awakeRatio", 0) - previous.get("awakeRatio", 0), 4)
    score_delta = round(current.get("sleepScore", 0) - previous.get("sleepScore", 0), 1)

    # 현재 상태에 대한 등급 평가
    deep_level = evaluate_status(current.get("deepSleepRatio", 0), {"good": 0.20, "warning": 0.13})
    rem_level = evaluate_status(current.get("remSleepRatio", 0), {"good": 0.22, "warning": 0.15})
    awake_level = evaluate_status(current.get("awakeRatio", 0), {"good": 0.10, "warning": 0.15})
    score_level = evaluate_status(current.get("sleepScore", 0), {"good": 80, "warning": 65})

    # 자연어 요약 문장 구성
    if rem_level == "bad":
        summary.append("렘수면 부족")
    if awake_level == "bad":
        summary.append("잦은 각성")
    if deep_level == "bad":
        summary.append("깊은 수면 부족")
    if score_level == "bad":
        summary.append("전반적인 수면 질 저하")

    summary_text = " 및 ".join(summary) + "이 관찰되었습니다." if summary else "수면 상태는 전반적으로 안정적입니다."

    print("[build_sleep_prompt] summary:", summary)
    return {
        "summary": summary_text,
        "improvement": {
            "score_delta": score_delta,
            "deep_delta": deep_delta,
            "awake_delta": awake_delta
        },
        "evaluation": {
            "deep": deep_level,
            "rem": rem_level,
            "awake": awake_level,
            "score": score_level
        }
    }