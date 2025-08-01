# app.py

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import os
from dotenv import load_dotenv

# .env 파일 로드 (import 전에 먼저 실행)
load_dotenv()

from services.recommender import recommend, recommend_with_sleep_data, recommend_with_both_data
from services.data_fetcher import data_fetcher

# API 키 확인
api_key = os.getenv("MAIN_SERVER_API_KEY")
if not api_key:
    print("⚠️  WARNING: MAIN_SERVER_API_KEY is not set!")
    print("   Please set the environment variable or add it to .env file")
else:
    print("✅ MAIN_SERVER_API_KEY is configured")

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
SLEEP_DATA_EXAMPLE = {
    "userId": "user123",
    "preferenceMode": "effectiveness",
    "preferredSounds": ["NATURE_1_WATER.mp3", "WHITE_2_UNDERWATER.mp3"],
    "previous": {
        "sleepScore": 68,
        "deepSleepRatio": 0.12,
        "remSleepRatio": 0.14,
        "awakeRatio": 0.18
    },
    "current": {
        "sleepScore": 75,
        "deepSleepRatio": 0.17,
        "remSleepRatio": 0.19,
        "awakeRatio": 0.13
    },
    "previousRecommendations": ["ASMR_2_HAIR.mp3", "ASMR_3_TAPPING.mp3", "FIRE_2.mp3"]
}

class SleepDataDto(BaseModel):
    userId: str
    preferenceMode: str = Field(..., example="effectiveness", description="추천 기준: preference / effectiveness")
    preferredSounds: List[str] = []
    previous: Dict[str, Any]
    current: Dict[str, Any]
    previousRecommendations: List[str] = []

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"value": SLEEP_DATA_EXAMPLE}
            ]
        }
    }

# 통합 추천 입력 스키마 (수면 데이터 + 설문 데이터)
class CombinedDataDto(BaseModel):
    userId: str
    preferenceMode: str = Field(..., example="effectiveness", description="추천 기준: preference / effectiveness")
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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "value": {
                        **SLEEP_DATA_EXAMPLE,
                        **USER_SURVEY_EXAMPLE
                    }
                }
            ]
        }
    }

# API 엔드포인트 정의
@app.post("/recommend", summary="설문 기반 수면 사운드 추천")
def get_recommendation(request: UserSurveyDto) -> Dict:
    user_input = request.dict()
    return recommend(user_input)

@app.post("/recommend/sleep", summary="수면 데이터 기반 수면 사운드 추천")
def get_sleep_based_recommendation(request: SleepDataDto) -> Dict:
    return recommend_with_sleep_data(request.dict())

@app.post("/recommend/combined", summary="수면 데이터 + 설문 데이터 기반 통합 추천")
def get_combined_recommendation(request: CombinedDataDto) -> Dict:
    return recommend_with_both_data(request.dict())

# 새로운 엔드포인트들 - 메인 서버에서 데이터 자동 가져오기
@app.get("/recommend/auto/{user_id}", summary="사용자 ID로 자동 데이터 가져와서 추천")
async def get_auto_recommendation(user_id: str, preference_mode: str = "effectiveness") -> Dict:
    """
    사용자 ID만으로 메인 서버에서 수면 데이터와 설문 데이터를 자동으로 가져와서 추천합니다.
    """
    try:
        # 메인 서버에서 통합 데이터 가져오기
        combined_data = await data_fetcher.fetch_combined_data(user_id)
        
        # preference_mode 추가
        combined_data["preferenceMode"] = preference_mode
        
        # 기본값 설정 (데이터가 없는 경우)
        if "preferredSounds" not in combined_data:
            combined_data["preferredSounds"] = []
        if "previousRecommendations" not in combined_data:
            combined_data["previousRecommendations"] = []
        
        # 통합 추천 실행
        return recommend_with_both_data(combined_data)
        
    except Exception as e:
        print(f"[Auto Recommendation] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get auto recommendation: {str(e)}"
        )

@app.get("/recommend/sleep-auto/{user_id}", summary="사용자 ID로 수면 데이터만 가져와서 추천")
async def get_sleep_auto_recommendation(user_id: str, preference_mode: str = "effectiveness") -> Dict:
    """
    사용자 ID만으로 메인 서버에서 수면 데이터를 자동으로 가져와서 추천합니다.
    """
    try:
        # 메인 서버에서 수면 데이터 가져오기
        sleep_data = await data_fetcher.fetch_sleep_data(user_id)
        
        # preference_mode 추가
        sleep_data["preferenceMode"] = preference_mode
        
        # 기본값 설정
        if "preferredSounds" not in sleep_data:
            sleep_data["preferredSounds"] = []
        if "previousRecommendations" not in sleep_data:
            sleep_data["previousRecommendations"] = []
        
        # 수면 데이터 기반 추천 실행
        return recommend_with_sleep_data(sleep_data)
        
    except Exception as e:
        print(f"[Sleep Auto Recommendation] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sleep auto recommendation: {str(e)}"
        )

@app.get("/recommend/survey-auto/{user_id}", summary="사용자 ID로 설문 데이터만 가져와서 추천")
async def get_survey_auto_recommendation(user_id: str) -> Dict:
    """
    사용자 ID만으로 메인 서버에서 설문 데이터를 자동으로 가져와서 추천합니다.
    """
    try:
        # 메인 서버에서 설문 데이터 가져오기
        survey_data = await data_fetcher.fetch_survey_data(user_id)
        
        # 설문 기반 추천 실행
        return recommend(survey_data)
        
    except Exception as e:
        print(f"[Survey Auto Recommendation] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get survey auto recommendation: {str(e)}"
        )

# 더 간단한 엔드포인트들 (예시 코드 스타일)
@app.get("/recommend/simple/{user_id}", summary="간단한 추천 - userId만으로")
async def get_simple_recommendation(user_id: str) -> Dict:
    """
    예시 코드처럼 userId만 받아서 추천하는 간단한 엔드포인트
    """
    try:
        # 메인 서버에서 데이터 가져오기
        combined_data = await data_fetcher.fetch_combined_data(user_id)
        
        # 기본 설정
        combined_data["preferenceMode"] = "effectiveness"
        combined_data["preferredSounds"] = combined_data.get("preferredSounds", [])
        combined_data["previousRecommendations"] = combined_data.get("previousRecommendations", [])
        
        # 추천 실행
        result = recommend_with_both_data(combined_data)
        
        return {
            "userId": user_id,
            "recommendation": result
        }
        
    except Exception as e:
        print(f"[Simple Recommendation] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get simple recommendation: {str(e)}"
        )

# 메인 서버에서 데이터를 받는 엔드포인트 (POST)
@app.post("/recommend/receive", summary="메인 서버에서 데이터를 받아서 추천")
async def receive_and_recommend(request: Request) -> Dict:
    """
    메인 서버가 보낸 데이터를 받아서 추천하는 엔드포인트
    """
    try:
        # 메인 서버가 보낸 JSON 데이터 받기
        data = await request.json()
        print(f"[Receive Recommendation] Received data: {data}")
        
        # 데이터 구조 확인 및 처리
        if "userId" not in data:
            raise HTTPException(status_code=400, detail="userId is required")
        
        # 추천 실행
        result = recommend_with_both_data(data)
        
        return result
        
    except Exception as e:
        print(f"[Receive Recommendation] Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process received data: {str(e)}"
        )

# 루트 엔드포인트 (상태 확인용)
@app.get("/", summary="서버 상태 확인")
def read_root():
    return {"message": "안녕하세요! 수면 사운드 추천 API 서버입니다."}