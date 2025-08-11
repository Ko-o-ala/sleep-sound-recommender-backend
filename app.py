# app.py

from fastapi import FastAPI, HTTPException, Request, Path, Query
from pydantic import BaseModel, Field
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
    description="""
    사용자의 수면 데이터와 설문조사 데이터를 기반으로 맞춤형 수면 사운드를 추천하는 API입니다.

    주요 기능:
    • 설문 데이터 기반 추천: 사용자 설문조사 결과를 바탕으로 추천 (첫 사용 시)
    • 통합 추천: 설문과 수면 데이터를 모두 활용한 추천 (수면 데이터 쌓인 후)

    사용 시나리오:
    • 첫 사용: 설문조사만으로 추천 (/recommend)
    • 수면 데이터 쌓인 후: 수면+설문 통합 추천 (/recommend/combined)
    """,
    version="1.0.0"
)

# 설문 응답 기반 입력 스키마
class UserSurveyDto(BaseModel):
    userID: str = Field(..., description="사용자 ID")
    date: str = Field(..., description="요청 날짜")
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
    preferenceBalance: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="선호도 vs 효과성 밸런스 (0.0=선호도 중심, 1.0=효과성 중심, 0.5=균형)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "userID": "seoin2744",
                    "date": "2025-07-15T00:00:00.000+00:00",
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
                    "preferenceBalance": 0.6
                }
            ]
        }
    }

# 통합 추천 입력 스키마 (수면 데이터 + 설문 데이터)
class CombinedDataDto(BaseModel):
    userID: str = Field(..., description="사용자 ID")
    date: str = Field(..., description="요청 날짜")
    preferredSounds: List[str] = []
    previous: Dict[str, Any]
    current: Dict[str, Any]
    previousRecommendations: List[str] = []
    # 설문 데이터 필드들
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
    screenTimeBeforeSleep: Optional[str] = None
    stressLevel: Optional[str] = None
    sleepGoal: Optional[str] = None
    preferredFeedbackFormat: Optional[str] = None
    preferenceBalance: Optional[int] = Field(default=5, ge=0, le=10, description="선호도 vs 효과성 밸런스 (0=선호도 중심, 10=효과성 중심, 5=균형)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "userID": "user123",
                    "date": "2025-07-15T00:00:00.000+00:00",
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
                    ],
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
                }
            ]
        }
    }

# API 엔드포인트 정의
@app.post(
    "/recommend", 
    tags=["추천 서비스"],
    summary="설문 기반 수면 사운드 추천",
    description="""
    사용자의 설문조사 데이터를 직접 전송받아 수면 사운드를 추천합니다.

    사용 시나리오: 클라이언트가 설문조사 데이터를 직접 가지고 있는 경우
    입력 데이터: 수면 선호도, 스트레스 레벨, 수면 목표 등 설문조사 결과
    추천 방식: RAG(Retrieval-Augmented Generation) 기반 유사도 검색 + LLM 개인화 텍스트 생성
    """,
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
    result = recommend(user_input)
    return {
        "userID": user_input.get("userID", "unknown"),
        "date": user_input.get("date", ""),
        "recommendation_text": result["recommendation_text"],
        "recommended_sounds": result["recommended_sounds"]
    }

@app.post(
    "/recommend/combined", 
    tags=["추천 서비스"],
    summary="수면 데이터 + 설문 데이터 기반 통합 추천",
    description="""
    수면 데이터와 설문 데이터를 모두 전송받아 통합적으로 수면 사운드를 추천합니다.
    기존 추천 결과의 유무에 따라 자동으로 적절한 추천 방식을 선택합니다.
    
    사용 시나리오: 클라이언트가 수면 데이터와 설문 데이터를 모두 가지고 있는 경우
    입력 데이터: 수면 패턴 정보 + 설문조사 결과 (기존 추천 결과는 선택사항)
    추천 방식: 
    • 기존 추천 결과가 있으면: 수면 데이터 분석 + 설문 선호도 반영 + 기존 추천 결과 학습
    • 기존 추천 결과가 없으면: 수면 데이터 분석 + 설문 선호도 반영 + 신규 추천 알고리즘
    """,
    response_model=RecommendResponse
)
def get_combined_recommendation(request: CombinedDataDto) -> Dict:
    """
    수면 데이터와 설문 데이터를 모두 활용하여 통합 추천을 제공합니다.
    기존 추천 결과의 유무에 따라 자동으로 적절한 추천 방식을 선택합니다.
    
    Args:
        request: 수면 데이터와 설문 데이터가 포함된 통합 데이터
        
    Returns:
        사용자 ID와 함께 상황에 맞는 추천 텍스트와 추천 사운드 목록
    """
    user_input = request.dict()
    
    # 기존 추천 결과가 있는지 자동 감지
    has_previous_recommendations = (
        hasattr(request, 'previousRecommendations') and 
        request.previousRecommendations and 
        len(request.previousRecommendations) > 0
    )
    
    result = recommend_with_both_data(
        user_input, 
        is_new_user=not has_previous_recommendations
    )
    
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