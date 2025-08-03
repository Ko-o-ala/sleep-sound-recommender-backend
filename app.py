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
    recommendation_text: str = Field(..., description="개인화된 추천 설명 텍스트")
    recommended_sounds: List[SoundRecommendation] = Field(..., description="추천된 사운드 목록")

class SimpleRecommendResponse(BaseModel):
    userId: str = Field(..., description="사용자 ID")
    recommendation: RecommendResponse = Field(..., description="추천 결과")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="수면 사운드 추천 API",
    description="""
    사용자의 수면 데이터와 설문조사 데이터를 기반으로 맞춤형 수면 사운드를 추천하는 API입니다.

    주요 기능:
    • 설문 데이터 기반 추천: 사용자 설문조사 결과를 바탕으로 추천 (첫 사용 시)
    • 통합 추천: 설문과 수면 데이터를 모두 활용한 추천 (수면 데이터 쌓인 후)
    • 메인 서버 연동: 메인 서버에서 데이터를 직접 전송받아 추천

    사용 시나리오:
    • 첫 사용: 설문조사만으로 추천 (/recommend)
    • 수면 데이터 쌓인 후: 수면+설문 통합 추천 (/recommend/combined)

    주의사항:
    • 이 API는 데이터가 도착했을 때만 추천을 수행합니다
    • 자동 데이터 가져오기 기능은 제공하지 않습니다
    • 메인 서버가 데이터를 모아서 추천 서버에 POST해야 합니다
    """,
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
        개인화된 추천 텍스트와 추천 사운드 목록
    """
    user_input = request.dict()
    return recommend(user_input)



@app.post(
    "/recommend/combined", 
    tags=["추천 서비스"],
    summary="수면 데이터 + 설문 데이터 기반 통합 추천",
    description="""
    수면 데이터와 설문 데이터를 모두 전송받아 통합적으로 수면 사운드를 추천합니다.
    
    사용 시나리오: 클라이언트가 수면 데이터와 설문 데이터를 모두 가지고 있는 경우
    입력 데이터: 수면 패턴 정보 + 설문조사 결과
    추천 방식: 수면 데이터 분석 + 설문 선호도 반영 + 통합 점수 계산
    """,
    response_model=RecommendResponse
)
def get_combined_recommendation(request: CombinedDataDto) -> Dict:
    """
    수면 데이터와 설문 데이터를 모두 활용하여 통합 추천을 제공합니다.
    
    Args:
        request: 수면 데이터와 설문 데이터가 모두 포함된 통합 데이터
        
    Returns:
        통합 분석 기반 추천 텍스트와 추천 사운드 목록
    """
    return recommend_with_both_data(request.dict())

@app.post(
    "/recommend/receive", 
    tags=["메인 서버 연동"],
    summary="메인 서버에서 데이터를 받아서 추천",
    description="""
    메인 서버가 보낸 데이터를 받아서 추천을 제공합니다.
    
    사용 시나리오: 메인 서버에서 직접 데이터를 전송하는 경우
    입력 데이터: 메인 서버가 전송하는 JSON 형태의 사용자 데이터
    특징: 메인 서버와의 직접적인 연동을 위한 엔드포인트
    """,
    response_model=RecommendResponse
)
async def receive_and_recommend(request: Request) -> Dict:
    """
    메인 서버가 보낸 데이터를 받아서 추천을 제공합니다.
    
    Args:
        request: 메인 서버가 전송한 JSON 데이터
        
    Returns:
        메인 서버 데이터 기반 추천 결과
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