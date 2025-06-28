# utils/prompt_builder.py

from typing import Dict, List, Optional

def build_prompt(user_survey: Dict[str, any]) -> str:
    """
    설문조사 dict를 바탕으로
    임베딩 모델이 이해하기 쉬운 영어문장(쿼리) 생성
    """

    phrases = []

    # 사용자의 주요 목표, 문제점 추출
    if goal := user_survey.get("sleepGoal"):
        phrases.append(f"wants to achive the goal of '{goal}'")
    if issues := user_survey.get("sleepIssues"):
        phrases.append(f"is experiencing sleep issues like '{', '.join(issues)}'")
    if stress := user_survey.get("stressLevel"):
        phrases.append(f"and has a '{stress}' stress level.")

    # 사용자의 선호도 추출
    if sound_pref := user_survey.get("preferredSleepSound"):
        phrases.append(f"They generally prefer '{sound_pref}' sounds.")
    if calming_sound := user_survey.get("calmingSoundType"):
        phrases.append(f"They find '{calming_sound}' sounds to be calming.")
    
    # 주요 생활 습관 추출
    if caffeine := user_survey.get("caffeineIntakeLevel"):
        phrases.append(f"Their caffeine intake is '{caffeine}'.")
    if screentime := user_survey.get("screenTimeBeforeSleep"):
        phrases.append(f"They have screen time of '{screentime}' before sleep.")

    # 모든 정보를 조합하여 최종 쿼리 생성
    if not phrases:
        return "A user seeking better sleep." # 정보가 아예 없을 경우 기본값

    # "A user who wants to 'stayAsleep', is experiencing issues like 'wakeOften', and has a 'high' stress level."
    # 와 같이 아주 구체적인 문장이 만들어짐!
    return "A user who " + " ".join(phrases)

if __name__ == "__main__":
    # 테스트용 mock 데이터
    mock_full_response = {
      "success": True,
      "data": {
        "sleepLightUsage": "moodLight",
        "lightColorTemperature": "warmYellow",
        "noisePreference": "other",
        "noisePreferenceOther": "팝송",
        "youtubeContentType": "other",
        "youtubeContentTypeOther": "아이돌 영상",
        "usualBedtime": "12to2am",
        "usualWakeupTime": "7to9am",
        "dayActivityType": "outdoor",
        "morningSunlightExposure": "sometimes",
        "napFrequency": "1to2perWeek",
        "napDuration": "15to30",
        "mostDrowsyTime": "afternoon",
        "averageSleepDuration": "4to6h",
        "sleepIssues": [
          "fallAsleepHard",
          "wakeOften",
          "nightmares"
        ],
        "emotionalSleepInterference": [
          "stress",
          "anxiety"
        ],
        "emotionalSleepInterferenceOther": "",
        "preferredSleepSound": "music",
        "calmingSoundType": "waves",
        "calmingSoundTypeOther": "",
        "sleepDevicesUsed": [
          "watch",
          "app"
        ],
        "soundAutoOffType": "autoDetect",
        "timeToFallAsleep": "over30min",
        "caffeineIntakeLevel": "1to2cups",
        "exerciseFrequency": "dailyMorning",
        "screenTimeBeforeSleep": "over1hour",
        "stressLevel": "medium",
        "sleepGoal": "stayAsleep",
        "preferredFeedbackFormat": "voice"
      }
    }

    # 2. 전체 데이터에서 우리가 진짜 필요한 'data' 부분만 꺼낸다.
    mock_survey_input = mock_full_response['data']

    # 3. 그 'data' 부분만 함수에 넣어서 테스트!
    generated_prompt = build_prompt(mock_survey_input)
    print("--- 생성된 RAG 검색용 쿼리 (테스트) ---")
    print(generated_prompt)