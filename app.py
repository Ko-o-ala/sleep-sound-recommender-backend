from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import List, Dict
from services.recommender import recommend

# app 생성
app = FastAPI(
    title="수면 사운드 추천 API",
    description="사용자의 기분과 상태에 따라 수면 사운드를 추천해주는 API입니다.",
    version="1.0.0"
)

# 입력 데이터 형식 정의
class UserRequest(BaseModel):
    goal: str = Field(..., example="빠르게 잠들고 싶어요", description="사용자의 목표")
    preference: List[str] = Field(..., example=["자연", "백색소음"], description="선호하는 사운드 카테고리")
    issues: str = Field(..., example="요즘 스트레스가 많고 뒤척임이 심해요", description="사용자의 현재 문제점")

# API 엔드포인트
@app.post("/recommend", summary="수면 사운드 추천")
def get_recommendation(request: UserRequest) -> Dict:
    # 사용자 입력을 받아서 RAG, LLM을 통해 맞춤형 수면 사운드, 추천 멘트 반환
    user_input = request.dict()
    result = recommend(user_input)
    return result

# root 엔드포인트
@app.get("/", summary="서버 상태 확인")
def read_root():
    return {"message": "안녕하세요! 수면 사운드 추천 API 서버입니다."}