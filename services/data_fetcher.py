# data_fetcher.py

import httpx
import os
from typing import Dict, Optional, Any
from fastapi import HTTPException

class DataFetcher:
    def __init__(self):
        # 메인 서버 URL (환경변수에서 가져오거나 기본값 사용)
        self.base_url = os.getenv("MAIN_SERVER_URL", "https://kooala.tassoo.uk")
        # API 키 (환경변수에서 가져와야 함)
        self.api_key = os.getenv("MAIN_SERVER_API_KEY")
        
        if not self.api_key:
            print("WARNING: MAIN_SERVER_API_KEY environment variable is not set!")
            print("   Using dummy data for testing...")
        
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        } if self.api_key else {"Content-Type": "application/json"}
    
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
            "preferredSounds": ["NATURE_1_WATER.mp3"],
            "previousRecommendations": ["ASMR_2_HAIR.mp3", "FIRE_2.mp3"]
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
        # API 키가 없으면 더미 데이터 반환
        if not self.api_key:
            print(f"[DataFetcher] No API key, using dummy sleep data for user {user_id}")
            return self._get_dummy_sleep_data(user_id)
        
        try:
            url = f"{self.base_url}/sleep-data/user/{user_id}/last"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                
                if response.status_code == 200:
                    raw_data = response.json()
                    data = self._parse_response(raw_data)
                    print(f"[DataFetcher] Sleep data fetched for user {user_id}: {data}")
                    return data
                else:
                    print(f"[DataFetcher] Failed to fetch sleep data. Status: {response.status_code}, Response: {response.text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to fetch sleep data from main server: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            print(f"[DataFetcher] Network error while fetching sleep data: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Network error while fetching sleep data: {str(e)}"
            )
        except Exception as e:
            print(f"[DataFetcher] Unexpected error while fetching sleep data: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while fetching sleep data: {str(e)}"
            )
    
    async def fetch_survey_data(self, user_id: str) -> Dict[str, Any]:
        """
        메인 서버에서 사용자의 설문조사 데이터를 가져옵니다.
        GET /users/survey/{userID}/result
        """
        # API 키가 없으면 더미 데이터 반환
        if not self.api_key:
            print(f"[DataFetcher] No API key, using dummy survey data for user {user_id}")
            return self._get_dummy_survey_data(user_id)
        
        try:
            url = f"{self.base_url}/users/survey/{user_id}/result"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                
                if response.status_code == 200:
                    raw_data = response.json()
                    data = self._parse_response(raw_data)
                    print(f"[DataFetcher] Survey data fetched for user {user_id}: {data}")
                    return data
                else:
                    print(f"[DataFetcher] Failed to fetch survey data. Status: {response.status_code}, Response: {response.text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to fetch survey data from main server: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            print(f"[DataFetcher] Network error while fetching survey data: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Network error while fetching survey data: {str(e)}"
            )
        except Exception as e:
            print(f"[DataFetcher] Unexpected error while fetching survey data: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error while fetching survey data: {str(e)}"
            )
    
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