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

    사용 시나리오:
    • 첫 사용: 설문조사만으로 추천 (/recommend)
    • 수면 데이터 쌓인 후: 수면+설문 통합 추천 (/recommend/combined)
    """,
    version="1.0.0"
)

# 예시 데이터
USER_SURVEY_EXAMPLE = {
    # === 설문조사 데이터 ===
    "sleepLightUsage": "none",                    # 수면 조명 사용 여부
    "lightColorTemperature": "warmYellow",        # 조명 색온도
    "noisePreference": "nature",                  # 소음 선호도
    "noisePreferenceOther": "팝송",               # 기타 소음 선호도
    "youtubeContentType": "none",                 # 유튜브 콘텐츠 타입
    "youtubeContentTypeOther": "아이돌 영상",     # 기타 유튜브 콘텐츠
    "usualBedtime": "12to2am",                   # 평소 취침 시간
    "usualWakeupTime": "7to9am",                 # 평소 기상 시간
    "dayActivityType": "outdoor",                 # 주간 활동 타입
    "morningSunlightExposure": "daily",          # 아침 햇빛 노출
    "napFrequency": "none",                       # 낮잠 빈도
    "napDuration": "none",                        # 낮잠 지속시간
    "mostDrowsyTime": "afternoon",               # 가장 졸린 시간
    "averageSleepDuration": "4to6h",             # 평균 수면 시간
    "sleepIssues": ["fallAsleepHard", "wakeOften"], # 수면 문제
    "emotionalSleepInterference": ["stress", "anxiety"], # 정서적 수면 방해
    "emotionalSleepInterferenceOther": "",        # 기타 정서적 방해
    "preferredSleepSound": "nature",              # 선호하는 수면 사운드
    "calmingSoundType": "rain",                   # 진정 사운드 타입
    "calmingSoundTypeOther": "",                  # 기타 진정 사운드
    "sleepDevicesUsed": [],                       # 사용하는 수면 기기
    "soundAutoOffType": "autoOff1hour",          # 사운드 자동 종료 타입
    "timeToFallAsleep": "over30min",             # 잠들기까지 시간
    "caffeineIntakeLevel": "none",                # 카페인 섭취 수준
    "exerciseFrequency": "sometimes",             # 운동 빈도
    "screenTimeBeforeSleep": "30minTo1hour",     # 취침 전 스크린 시간
    "stressLevel": "high",                        # 스트레스 수준
    "sleepGoal": "improveSleepQuality",          # 수면 목표
    "preferredFeedbackFormat": "text",            # 선호하는 피드백 형식
    
    # === 추천 기준 설정 ===
    "preferenceBalance": 7                        # 선호도 vs 효과성 밸런스 (0~10)
}

SLEEP_DATA_EXAMPLE = {
    # === 기본 정보 ===
    "userId": "user123",                          # 사용자 ID
    
    # === 수면 데이터 ===
    "preferredSounds": [                          # 사용자가 좋아한 사운드들 (3개)
        "NATURE_1_WATER.mp3",                    # 계곡물 흐름
        "WHITE_2_UNDERWATER.mp3",                # 수중 백색소음
        "ASMR_2_HAIR.mp3"                        # 머리카락 빗는 소리
    ],
    "previous": {                                 # 이전 수면 데이터
        "sleepScore": 68,                         # 이전 수면 점수
        "deepSleepRatio": 0.12,                   # 이전 깊은 수면 비율
        "remSleepRatio": 0.14,                    # 이전 REM 수면 비율
        "lightSleepRatio": 0.56,                  # 이전 얕은 수면 비율
        "awakeRatio": 0.18                        # 이전 각성 비율
    },
    "current": {                                  # 현재 수면 데이터
        "sleepScore": 75,                         # 현재 수면 점수
        "deepSleepRatio": 0.17,                   # 현재 깊은 수면 비율
        "remSleepRatio": 0.19,                    # 현재 REM 수면 비율
        "lightSleepRatio": 0.51,                  # 현재 얕은 수면 비율
        "awakeRatio": 0.13                        # 현재 각성 비율
    },
    "previousRecommendations": [                  # 이전 추천 사운드들 (3개)
        "ASMR_2_HAIR.mp3",                       # 머리카락 빗는 소리
        "ASMR_3_TAPPING.mp3",                    # 손가락 두드림
        "FIRE_2.mp3"                             # 불 소리
    ]
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
    preferenceBalance: Optional[int] = Field(default=5, ge=0, le=10, description="선호도 vs 효과성 밸런스 (0=선호도 중심, 10=효과성 중심, 5=균형)")

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