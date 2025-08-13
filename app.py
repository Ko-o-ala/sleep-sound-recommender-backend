# app.py

from fastapi import FastAPI, HTTPException, Request, Path, Query
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv

# .env 파일 로드 (import 전에 먼저 실행)
load_dotenv()

from services.recommender import recommend, recommend_with_both_data
from services.data_fetcher import data_fetcher

# API 키 확인
api_key = os.getenv("MAIN_SERVER_API_KEY")
if not api_key:
    print("⚠️  WARNING: MAIN_SERVER_API_KEY is not set!")
    print("   Please set the environment variable or add it to .env file")
else:
    print("✅ MAIN_SERVER_API_KEY is configured")

# 응답 모델 정의
class SoundRecommendation(BaseModel):
    filename: str = Field(..., description="사운드 파일명")
    rank: int = Field(..., description="추천 순위 (1부터 시작)")
    preference: str = Field(..., description="사용자 선호도 (top/none)")

class RecommendResponse(BaseModel):
    userID: str = Field(..., description="사용자 ID")
    date: str = Field(..., description="요청 날짜")
    recommendation_text: str = Field(..., description="개인화된 추천 설명 텍스트")
    recommended_sounds: List[SoundRecommendation] = Field(..., description="추천된 사운드 목록")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="수면 사운드 추천 API",
    version="1.0.0"
)

# 설문조사 데이터 스키마
class SurveyData(BaseModel):
    sleepLightUsage: Optional[str] = None
    lightColorTemperature: Optional[str] = None
    noisePreference: Optional[str] = None
    noisePreferenceOther: Optional[str] = None
    youtubeContentType: Optional[str] = None
    youtubeContentTypeOther: Optional[str] = None
    usualBedtime: Optional[str] = None
    usualWakeupTime: Optional[str] = None
    dayActivityType: Optional[str] = None
    morningSunlightExposure: Optional[str] = None
    napFrequency: Optional[str] = None
    napDuration: Optional[str] = None
    mostDrowsyTime: Optional[str] = None
    averageSleepDuration: Optional[str] = None
    sleepIssues: Optional[List[str]] = None
    emotionalSleepInterference: Optional[List[str]] = None
    emotionalSleepInterferenceOther: Optional[str] = None
    preferredSleepSound: Optional[str] = None
    calmingSoundType: Optional[str] = None
    calmingSoundTypeOther: Optional[str] = None
    sleepDevicesUsed: Optional[List[str]] = None
    soundAutoOffType: Optional[str] = None
    timeToFallAsleep: Optional[str] = None
    caffeineIntakeLevel: Optional[str] = None
    exerciseFrequency: Optional[str] = None
    exerciseWhen: Optional[str] = None
    screenTimeBeforeSleep: Optional[str] = None
    stressLevel: Optional[str] = None
    sleepGoal: Optional[List[str]] = None
    preferredFeedbackFormat: Optional[str] = None
    preferenceBalance: Optional[int] = Field(default=5, ge=0, le=10, description="선호도 vs 효과성 밸런스 (0=선호도 중심, 10=효과성 중심, 5=균형)")

# 수면 데이터 스키마
class SleepData(BaseModel):
    preferredSounds: List[str] = []
    previous: Dict[str, Any]
    current: Dict[str, Any]
    previousRecommendations: List[str] = []

# 설문 응답 기반 입력 스키마 (설문조사 데이터만)
class UserSurveyDto(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "userID": "seoin2744",
                    "date": "2025-07-15T00:00:00.000+00:00",
                    "survey": {
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
                        "sleepIssues": ["fallAsleepHard", "wakeOften", "nightmares"],
                        "emotionalSleepInterference": ["stress", "anxiety"],
                        "emotionalSleepInterferenceOther": "",
                        "preferredSleepSound": "music",
                        "calmingSoundType": "waves",
                        "calmingSoundTypeOther": "",
                        "sleepDevicesUsed": ["watch", "app"],
                        "soundAutoOffType": "autoOff1hour",
                        "timeToFallAsleep": "over30min",
                        "caffeineIntakeLevel": "1to2cups",
                        "exerciseFrequency": "daily",
                        "exerciseWhen": "morning",
                        "screenTimeBeforeSleep": "over1hour",
                        "stressLevel": "medium",
                        "sleepGoal": ["fallAsleepFast", "stayAsleep"],
                        "preferredFeedbackFormat": "text",
                        "preferenceBalance": 6
                    }
                }
            ]
        },
        json_schema_serialization_defaults=True,
        populate_by_name=True
    )
    
    userID: str = Field(..., description="사용자 ID")
    date: str = Field(..., description="요청 날짜")
    survey: SurveyData

# 통합 추천 입력 스키마 (수면 데이터 + 설문 데이터)
class CombinedDataDto(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "userID": "user123",
                    "date": "2025-07-15T00:00:00.000+00:00",
                    "survey": {
                        "sleepLightUsage": "none",
                        "lightColorTemperature": "warmYellow",
                        "noisePreference": "nature",
                        "noisePreferenceOther": "팝송",
                        "youtubeContentType": "none",
                        "youtubeContentTypeOther": "아이돌 영상",
                        "usualBedtime": "12to2am",
                        "usualWakeupTime": "7to9am",
                        "dayActivityType": "outdoor",
                        "morningSunlightExposure": "daily",
                        "napFrequency": "none",
                        "napDuration": "none",
                        "mostDrowsyTime": "afternoon",
                        "averageSleepDuration": "4to6h",
                        "sleepIssues": ["fallAsleepHard", "wakeOften"],
                        "emotionalSleepInterference": ["stress", "anxiety"],
                        "emotionalSleepInterferenceOther": "",
                        "preferredSleepSound": "nature",
                        "calmingSoundType": "rain",
                        "calmingSoundTypeOther": "",
                        "sleepDevicesUsed": [],
                        "soundAutoOffType": "autoOff1hour",
                        "timeToFallAsleep": "over30min",
                        "caffeineIntakeLevel": "none",
                        "exerciseFrequency": "sometimes",
                        "screenTimeBeforeSleep": "30minTo1hour",
                        "stressLevel": "high",
                        "sleepGoal": "improveSleepQuality",
                        "preferredFeedbackFormat": "text",
                        "preferenceBalance": 7
                    },
                    "sleepData": {
                        "preferredSounds": [
                            "NATURE_1_WATER.mp3",
                            "WHITE_2_UNDERWATER.mp3",
                            "ASMR_2_HAIR.mp3"
                        ],
                        "previous": {
                            "sleepScore": 68,
                            "deepSleepRatio": 0.12,
                            "remSleepRatio": 0.14,
                            "lightSleepRatio": 0.56,
                            "awakeRatio": 0.18
                        },
                        "current": {
                            "sleepScore": 75,
                            "deepSleepRatio": 0.17,
                            "remSleepRatio": 0.19,
                            "lightSleepRatio": 0.51,
                            "awakeRatio": 0.13
                        },
                        "previousRecommendations": [
                            "ASMR_2_HAIR.mp3",
                            "ASMR_3_TAPPING.mp3",
                            "FIRE_2.mp3"
                        ]
                    }
                }
            ]
        },
        json_schema_serialization_defaults=True,
        populate_by_name=True
    )
    
    userID: str = Field(..., description="사용자 ID")
    date: str = Field(..., description="요청 날짜")
    survey: SurveyData
    sleepData: SleepData

# API 엔드포인트 정의
@app.post(
    "/recommend", 
    tags=["추천 서비스"],
    summary="설문 기반 수면 사운드 추천 (설문조사 데이터만)",
    description="사용자의 설문조사 데이터만을 전송받아 수면 사운드를 추천합니다. 사용 시나리오: 클라이언트가 설문조사 데이터만 가지고 있는 경우 (첫 사용자). 입력 데이터: 수면 선호도, 스트레스 레벨, 수면 목표 등 설문조사 결과. 추천 방식: RAG(Retrieval-Augmented Generation) 기반 유사도 검색 + LLM 개인화 텍스트 생성",
    response_model=RecommendResponse
)
def get_recommendation(request: UserSurveyDto) -> Dict:
    """
    설문조사 데이터를 기반으로 수면 사운드를 추천합니다.
    
    Args:
        request: 사용자 설문조사 데이터
        
    Returns:
        사용자 ID와 함께 개인화된 추천 텍스트와 추천 사운드 목록
    """
    user_input = request.dict()
    # survey 데이터를 최상위로 평탄화
    survey_data = user_input.get("survey", {})
    user_input.update(survey_data)
    del user_input["survey"]
    
    result = recommend(user_input)
    return {
        "userID": user_input.get("userID", "unknown"),
        "date": user_input.get("date", ""),
        "recommendation_text": result["recommendation_text"],
        "recommended_sounds": result["recommended_sounds"]
    }

@app.post(
    "/recommend/combined/new", 
    tags=["추천 서비스"],
    summary="수면 데이터 + 설문 데이터 기반 통합 추천 (기존 추천결과 없음)",
    description="수면 데이터와 설문 데이터를 모두 전송받아 첫 번째 추천을 제공합니다. 사용 시나리오: 클라이언트가 수면 데이터와 설문 데이터를 모두 가지고 있지만, 기존 추천 결과가 없는 경우. 입력 데이터: 수면 패턴 정보 + 설문조사 결과 (previousRecommendations 필드 제외). 추천 방식: 수면 데이터 분석 + 설문 선호도 반영 + 신규 추천 알고리즘",
    response_model=RecommendResponse
)
def get_new_combined_recommendation(request: CombinedDataDto) -> Dict:
    """
    수면 데이터와 설문 데이터를 활용하여 첫 번째 추천을 제공합니다.
    기존 추천 결과가 없는 경우를 위한 엔드포인트입니다.
    
    Args:
        request: 수면 데이터와 설문 데이터가 포함된 통합 데이터 (previousRecommendations는 빈 배열)
        
    Returns:
        사용자 ID와 함께 신규 추천 알고리즘 기반 추천 텍스트와 추천 사운드 목록
    """
    user_input = request.dict()
    
    # survey와 sleepData를 최상위로 평탄화
    survey_data = user_input.get("survey", {})
    sleep_data = user_input.get("sleepData", {})
    user_input.update(survey_data)
    user_input.update(sleep_data)
    del user_input["survey"]
    del user_input["sleepData"]
    
    # previousRecommendations가 비어있거나 없는 경우를 확인
    if not user_input.get("previousRecommendations") or len(user_input.get("previousRecommendations", [])) == 0:
        result = recommend_with_both_data(user_input, is_new_user=True)
    else:
        # 만약 previousRecommendations가 있으면 기존 로직 사용
        result = recommend_with_both_data(user_input, is_new_user=False)
    
    return {
        "userID": user_input.get("userID", "unknown"),
        "date": user_input.get("date", ""),
        "recommendation_text": result["recommendation_text"],
        "recommended_sounds": result["recommended_sounds"]
    }

@app.post(
    "/recommend/combined", 
    tags=["추천 서비스"],
    summary="수면 데이터 + 설문 데이터 + 기존 추천결과 기반 통합 추천",
    description="수면 데이터, 설문 데이터, 기존 추천 결과를 모두 전송받아 추천을 업데이트합니다. 사용 시나리오: 클라이언트가 수면 데이터, 설문 데이터, 기존 추천 결과를 모두 가지고 있는 경우. 입력 데이터: 수면 패턴 정보 + 설문조사 결과 + 기존 추천 결과 (previousRecommendations 필드 필수). 추천 방식: 수면 데이터 분석 + 설문 선호도 반영 + 기존 추천 결과 학습 + 개선된 추천 알고리즘",
    response_model=RecommendResponse
)
def get_combined_recommendation(request: CombinedDataDto) -> Dict:
    """
    수면 데이터, 설문 데이터, 기존 추천 결과를 모두 활용하여 추천을 업데이트합니다.
    기존 추천 결과가 있는 경우를 위한 엔드포인트입니다.
    
    Args:
        request: 수면 데이터, 설문 데이터, 기존 추천 결과가 모두 포함된 통합 데이터
        
    Returns:
        사용자 ID와 함께 기존 추천 결과를 학습한 개선된 추천 텍스트와 추천 사운드 목록
    """
    user_input = request.dict()
    
    # survey와 sleepData를 최상위로 평탄화
    survey_data = user_input.get("survey", {})
    sleep_data = user_input.get("sleepData", {})
    user_input.update(survey_data)
    user_input.update(sleep_data)
    del user_input["survey"]
    del user_input["sleepData"]
    
    # previousRecommendations가 있는지 확인
    if user_input.get("previousRecommendations") and len(user_input.get("previousRecommendations", [])) > 0:
        result = recommend_with_both_data(user_input, is_new_user=False)
    else:
        # 만약 previousRecommendations가 없으면 신규 로직 사용
        result = recommend_with_both_data(user_input, is_new_user=True)
    
    return {
        "userID": user_input.get("userID", "unknown"),
        "date": user_input.get("date", ""),
        "recommendation_text": result["recommendation_text"],
        "recommended_sounds": result["recommended_sounds"]
    }

# 루트 엔드포인트 (상태 확인용)
@app.get(
    "/", 
    tags=["시스템"],
    summary="서버 상태 확인",
    description="API 서버의 현재 상태를 확인합니다."
)
def read_root():
    """
    서버 상태를 확인합니다.
    
    Returns:
        서버 상태 메시지
    """
    return {"message": "안녕하세요! 수면 사운드 추천 API 서버입니다."}