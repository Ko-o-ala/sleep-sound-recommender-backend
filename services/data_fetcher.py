# data_fetcher.py

import httpx
import os
from typing import Dict, Optional, Any
from fastapi import HTTPException

class DataFetcher:
    def __init__(self):
        # 메인 서버 URL (환경변수에서 가져오거나 기본값 사용)
        self.base_url = os.getenv("MAIN_SERVER_URL", "https://kooala.tassoo.uk")
        # API 키 (더 이상 필요하지 않음)
        self.api_key = None
        
        self.headers = {"Content-Type": "application/json"}
    
    def _get_dummy_sleep_data(self, user_id: str) -> Dict[str, Any]:
        """API 키가 없을 때 사용할 더미 수면 데이터"""
        return {
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
            "preferredSounds": ["NATURE_1_WATER.mp3", "WHITE_2_UNDERWATER.mp3", "ASMR_2_HAIR.mp3"],
            "previousRecommendations": ["ASMR_2_HAIR.mp3", "ASMR_3_TAPPING.mp3", "FIRE_2.mp3"]
        }
    
    def _get_dummy_survey_data(self, user_id: str) -> Dict[str, Any]:
        """API 키가 없을 때 사용할 더미 설문 데이터"""
        return {
            "sleepLightUsage": "moodLight",
            "lightColorTemperature": "warmYellow",
                    "noisePreference": "other",
        "noisePreferenceOther": "파소",
        "youtubeContentType": "none",
        "youtubeContentTypeOther": "",
            "usualBedtime": "12to2am",
            "usualWakeupTime": "7to9am",
            "dayActivityType": "outdoor",
            "morningSunlightExposure": "daily",
            "napFrequency": "none",
            "napDuration": "none",
            "mostDrowsyTime": "afternoon",
            "averageSleepDuration": "4to6h",
            "sleepIssues": ["fallAsleepHard"],
            "emotionalSleepInterference": ["stress"],
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
    
    def _parse_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        메인 서버 응답을 파싱합니다.
        응답이 {"success": true, "data": {...}} 형태일 수 있음
        """
        if isinstance(response_data, dict):
            if "success" in response_data and "data" in response_data:
                # {"success": true, "data": {...}} 형태
                return response_data["data"]
            else:
                # 직접 데이터 형태
                return response_data
        return response_data
    
    async def fetch_sleep_data(self, user_id: str) -> Dict[str, Any]:
        """
        메인 서버에서 사용자의 수면 데이터를 가져옵니다.
        GET /sleep-data/user/{userID}/last
        """
        # 더미 데이터 반환 (메인서버에서 직접 데이터를 보내므로)
        print(f"[DataFetcher] Using dummy sleep data for user {user_id}")
        return self._get_dummy_sleep_data(user_id)
    
    async def fetch_survey_data(self, user_id: str) -> Dict[str, Any]:
        """
        메인 서버에서 사용자의 설문조사 데이터를 가져옵니다.
        GET /users/survey/{userID}/result
        """
        # 더미 데이터 반환 (메인서버에서 직접 데이터를 보내므로)
        print(f"[DataFetcher] Using dummy survey data for user {user_id}")
        return self._get_dummy_survey_data(user_id)
    
    async def fetch_combined_data(self, user_id: str) -> Dict[str, Any]:
        """
        수면 데이터와 설문 데이터를 모두 가져와서 통합합니다.
        """
        try:
            # 병렬로 두 데이터를 동시에 가져오기
            import asyncio
            
            sleep_task = asyncio.create_task(self.fetch_sleep_data(user_id))
            survey_task = asyncio.create_task(self.fetch_survey_data(user_id))
            
            sleep_data, survey_data = await asyncio.gather(sleep_task, survey_task)
            
            # 데이터 통합 - 더 안전한 방식으로
            combined_data = {
                "userId": user_id,
                # 수면 데이터 필드들
                "previous": sleep_data.get("previous", {}),
                "current": sleep_data.get("current", {}),
                "preferredSounds": sleep_data.get("preferredSounds", []),
                "previousRecommendations": sleep_data.get("previousRecommendations", []),
                # 설문 데이터 필드들 (이미지에서 본 구조)
                "sleepLightUsage": survey_data.get("sleepLightUsage"),
                "lightColorTemperature": survey_data.get("lightColorTemperature"),
                "noisePreference": survey_data.get("noisePreference"),
                "noisePreferenceOther": survey_data.get("noisePreferenceOther"),
                "youtubeContentType": survey_data.get("youtubeContentType"),
                "youtubeContentTypeOther": survey_data.get("youtubeContentTypeOther"),
                "usualBedtime": survey_data.get("usualBedtime"),
                "usualWakeupTime": survey_data.get("usualWakeupTime"),
                "dayActivityType": survey_data.get("dayActivityType"),
                "morningSunlightExposure": survey_data.get("morningSunlightExposure"),
                "napFrequency": survey_data.get("napFrequency"),
                "napDuration": survey_data.get("napDuration"),
                "mostDrowsyTime": survey_data.get("mostDrowsyTime"),
                "averageSleepDuration": survey_data.get("averageSleepDuration"),
                "sleepIssues": survey_data.get("sleepIssues", []),
                "emotionalSleepInterference": survey_data.get("emotionalSleepInterference", []),
                "emotionalSleepInterferenceOther": survey_data.get("emotionalSleepInterferenceOther"),
                "preferredSleepSound": survey_data.get("preferredSleepSound"),
                "calmingSoundType": survey_data.get("calmingSoundType"),
                "calmingSoundTypeOther": survey_data.get("calmingSoundTypeOther"),
                "sleepDevicesUsed": survey_data.get("sleepDevicesUsed", []),
                "soundAutoOffType": survey_data.get("soundAutoOffType"),
                "timeToFallAsleep": survey_data.get("timeToFallAsleep"),
                "caffeineIntakeLevel": survey_data.get("caffeineIntakeLevel"),
                "exerciseFrequency": survey_data.get("exerciseFrequency"),
                "screenTimeBeforeSleep": survey_data.get("screenTimeBeforeSleep"),
                "stressLevel": survey_data.get("stressLevel"),
                "sleepGoal": survey_data.get("sleepGoal"),
                "preferredFeedbackFormat": survey_data.get("preferredFeedbackFormat")
            }
            
            print(f"[DataFetcher] Combined data for user {user_id}: {combined_data}")
            return combined_data
            
        except Exception as e:
            print(f"[DataFetcher] Error fetching combined data: {e}")
            raise

# 전역 인스턴스 생성
data_fetcher = DataFetcher() 