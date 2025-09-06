# prompt_builder.py
# AASM(미국수면의학회) 공식 가이드라인 기반 수면지표 평가 시스템
# 
# 수면 단계별 정상 비율 (총 수면 시간 대비):
# - 깊은 수면(N3): 13-23% (20%↑ 우수, 13%↓ 경고)
# - 렘수면(REM): 20-25% (22%↑ 우수, 20%↓ 경고)  
# - 총 얕은 수면(N1+N2): 40-60% (50% 근처 우수, 40%↓ 경고)
# - 각성(WASO): 15% 미만 정상 (10%↓ 우수, 15%↑ 경고)
# - 수면 점수: 80점↑ 좋음, 65-80점 애매, 65점↓ 나쁨

from typing import Dict, List, Optional
from services.llm_service import translate_korean_to_english

# 설문 응답 데이터를 자연어 영어 문장으로 바꿔서 LLM에게 넘겨줄 프롬프트 생성
def build_prompt(user_survey: Dict[str, any]) -> str:
    phrases = []

    # 1. 한글이 포함될 수 있는 기타 항목 추출 (값이 없을 경우 빈 문자열로 대체함)
    noise_other = user_survey.get("noisePreferenceOther") or ""

    # 2. 번역 수행 (한글 -> 영어)
    translated_noise_other = translate_korean_to_english(noise_other)

    # 3. 주요 필드를 더 구체적으로 문장으로 조립
    if goal := user_survey.get("sleepGoal"):
        if isinstance(goal, list):
            goal_text = ", ".join(goal)
        else:
            goal_text = goal
        phrases.append(f"wants to achieve the goal of '{goal_text}'")
    
    if issues := user_survey.get("sleepIssues"):
        if isinstance(issues, list):
            issues_text = ", ".join(issues)
        else:
            issues_text = issues
        phrases.append(f"is experiencing sleep issues like '{issues_text}'")
    
    if stress := user_survey.get("stressLevel"):
        phrases.append(f"and has a '{stress}' stress level.")
    
    if calming_type := user_survey.get("calmingSoundType"):
        phrases.append(f"They find '{calming_type}' sounds most calming.")
    
    if translated_noise_other:
        phrases.append(f"and also likes '{translated_noise_other}'.")
    
    # 추가적인 구체적인 정보들
    if bedtime := user_survey.get("usualBedtime"):
        phrases.append(f"They usually go to bed around '{bedtime}'.")
    
    if wakeup := user_survey.get("usualWakeupTime"):
        phrases.append(f"They usually wake up around '{wakeup}'.")
    
    if activity := user_survey.get("dayActivityType"):
        phrases.append(f"They have '{activity}' daily activities.")
    
    if caffeine := user_survey.get("caffeineIntakeLevel"):
        phrases.append(f"They consume '{caffeine}' caffeine.")
    
    if exercise := user_survey.get("exerciseFrequency"):
        phrases.append(f"They exercise '{exercise}'.")
    
    if screen_time := user_survey.get("screenTimeBeforeSleep"):
        phrases.append(f"They use screens '{screen_time}' before sleep.")

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



# 수면 데이터와 설문 데이터를 모두 사용하는 통합 프롬프트 생성
def build_combined_prompt(sleep_data: Dict, survey_data: Dict) -> Dict:
    print("[build_combined_prompt] sleep_data:", sleep_data)
    print("[build_combined_prompt] survey_data:", survey_data)
    
    # 1. 수면 데이터 기반 요약 생성
    previous = sleep_data.get("previous")  # None일 수 있음
    current = sleep_data["current"]
    
    summary = []
    
    # 현재 상태에 대한 등급 평가 (AASM 공식 가이드라인 기준)
    # 깊은 수면: 13-23%가 정상, 20% 이상은 우수, 13% 미만은 경고
    deep_level = evaluate_status(current.get("deepSleepRatio", 0), {"good": 0.20, "warning": 0.13})
    # 렘수면: 20-25%가 정상, 22% 이상은 우수, 20% 미만은 경고
    rem_level = evaluate_status(current.get("remSleepRatio", 0), {"good": 0.22, "warning": 0.20})
    # 총 얕은 수면(N1+N2): 40-60%가 정상, 50% 근처가 우수, 40% 미만은 경고
    light_level = evaluate_status(current.get("lightSleepRatio", 0), {"good": 0.50, "warning": 0.40})
    # 각성: 15% 미만이 정상, 10% 이하면 우수, 15% 이상은 경고
    awake_level = evaluate_status(current.get("awakeRatio", 0), {"good": 0.10, "warning": 0.15})
    # 수면 점수: 80점 이상은 좋음, 65-80점은 애매, 65점 미만은 나쁨
    score_level = evaluate_status(current.get("sleepScore", 0), {"good": 80, "warning": 65})
    
    # 자연어 요약 문장 구성
    if rem_level == "bad":
        summary.append("렘수면 부족")
    if awake_level == "bad":
        summary.append("잦은 각성")
    if deep_level == "bad":
        summary.append("깊은 수면 부족")
    if light_level == "bad":
        summary.append("얕은 수면 부족")
    if score_level == "bad":
        summary.append("전반적인 수면 질 저하")
    
    # previous 데이터가 없는 경우 추가 설명
    if not previous:
        summary.append("첫 번째 수면 데이터 수집")
    
    sleep_summary_text = " 및 ".join(summary) + "이 관찰되었습니다." if summary else "수면 상태는 전반적으로 안정적입니다."
    
    # previous 데이터가 있는 경우에만 변화량 계산
    if previous:
        # 변화량 계산
        deep_delta = round(current.get("deepSleepRatio", 0) - previous.get("deepSleepRatio", 0), 4)
        rem_delta = round(current.get("remSleepRatio", 0) - previous.get("remSleepRatio", 0), 4)
        light_delta = round(current.get("lightSleepRatio", 0) - previous.get("lightSleepRatio", 0), 4)
        awake_delta = round(current.get("awakeRatio", 0) - previous.get("awakeRatio", 0), 4)
        score_delta = round(current.get("sleepScore", 0) - previous.get("sleepScore", 0), 1)
        
        sleep_summary = {
            "summary": sleep_summary_text,
            "improvement": {
                "score_delta": score_delta,
                "deep_delta": deep_delta,
                "light_delta": light_delta,
                "awake_delta": awake_delta
            },
            "evaluation": {
                "deep": deep_level,
                "rem": rem_level,
                "light": light_level,
                "awake": awake_level,
                "score": score_level
            }
        }
    else:
        # previous 데이터가 없는 경우 변화량 정보 없이 생성
        sleep_summary = {
            "summary": sleep_summary_text,
            "evaluation": {
                "deep": deep_level,
                "rem": rem_level,
                "light": light_level,
                "awake": awake_level,
                "score": score_level
            }
        }
    
    # 2. 설문 데이터 기반 요약 생성
    survey_summary = build_prompt(survey_data)
    
    # 3. 통합 요약 생성
    combined_summary = f"{sleep_summary['summary']} {survey_summary}"
    
    print("[build_combined_prompt] combined_summary:", combined_summary)
    
    return {
        "summary": combined_summary,
        "sleep_summary": sleep_summary,
        "survey_summary": survey_summary,
        "improvement": sleep_summary.get("improvement", {}),
        "evaluation": sleep_summary.get("evaluation", {})
    }