# app.py

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from services.recommender import recommend, recommend_with_sleep_data

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="수면 사운드 추천 API",
    description="사용자의 상태 및 수면 데이터를 기반으로 사운드를 추천하는 API입니다.",
    version="1.0.0"
)

# 예시 데이터
USER_SURVEY_EXAMPLE = {
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
    "preferredFeedbackFormat": "text"
}

# 설문 응답 기반 입력 스키마
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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"value": USER_SURVEY_EXAMPLE}
            ]
        }
    }

# 수면 데이터 기반 추천 입력 스키마
class SleepDataDto(BaseModel):
    userId: str
    preferenceMode: str = Field(..., example="effectiveness", description="추천 기준: preference / effectiveness")
    preferredSounds: List[str] = []
    previous: Dict[str, any]
    current: Dict[str, any]
    previousRecommendations: List[str] = []

# API 엔드포인트 정의
@app.post("/recommend", summary="설문 기반 수면 사운드 추천")
def get_recommendation(request: UserSurveyDto) -> Dict:
    user_input = request.dict()
    return recommend(user_input)

@app.post("/recommend/sleep", summary="수면 데이터 기반 수면 사운드 추천")
def get_sleep_based_recommendation(request: SleepDataDto) -> Dict:
    return recommend_with_sleep_data(request.dict())

# 루트 엔드포인트 (상태 확인용)
@app.get("/", summary="서버 상태 확인")
def read_root():
    return {"message": "안녕하세요! 수면 사운드 추천 API 서버입니다."}