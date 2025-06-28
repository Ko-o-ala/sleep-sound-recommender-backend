from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from services.recommender import recommend

# app 생성
app = FastAPI(
    title="수면 사운드 추천 API",
    description="사용자의 기분과 상태에 따라 수면 사운드를 추천해주는 API입니다.",
    version="1.0.0"
)

# 입력 데이터 형식 정의
"""
class UserRequest(BaseModel):
    goal: str = Field(..., example="빠르게 잠들고 싶어요", description="사용자의 목표")
    preference: List[str] = Field(..., example=["자연", "백색소음"], description="선호하는 사운드 카테고리")
    issues: str = Field(..., example="요즘 스트레스가 많고 뒤척임이 심해요", description="사용자의 현재 문제점")
"""

# 메인서버의 UserSurveyDto 스키마 반영
class UserSurveyDto(BaseModel):
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

# API 엔드포인트
@app.post("/recommend", summary="수면 사운드 추천")
def get_recommendation(request: UserSurveyDto) -> Dict:
    # 사용자 입력을 받아서 RAG, LLM을 통해 맞춤형 수면 사운드, 추천 멘트 반환
    user_input = request.dict()
    result = recommend(user_input)
    return result

# root 엔드포인트
@app.get("/", summary="서버 상태 확인")
def read_root():
    return {"message": "안녕하세요! 수면 사운드 추천 API 서버입니다."}