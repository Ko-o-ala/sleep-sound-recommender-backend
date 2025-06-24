import os
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv

# API 키
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_recommendation_text(user_prompt: str, sound_results: List[Dict]) -> str:
    # LLM의 역할 정하기
    system_message = (
        "너는 사용자의 현재 상황과 기분에 공감하며, 가장 적절한 수면 사운드를 다정하게 추천해주는 전문가야. "
        "주어진 사운드 목록 중에서 가장 적합한 1~2개를 골라, 왜 그 사운드가 사용자에게 도움이 될지 구체적인 이유를 들어 설명해줘."
    )

    # RAG가 찾아준 사운드 목록을 텍스트로 변환
    sound_list_text = "\n".join([
        f"- 제목: {sound['title']}, 설명: {sound['description']}" for sound in sound_results
    ])

    # LLM에게 전달할 최종 프롬프트
    final_prompt = (
        f"아래는 사용자의 현재 상태와, 그에 맞춰 1차로 추천된 사운드 목록이야.\n\n"
        f"--- 사용자 상태 ---\n{user_prompt}\n\n"
        f"--- 추천 사운드 목록 ---\n{sound_list_text}\n\n"
        f"이 정보를 바탕으로, 사용자만을 위한 따뜻하고 설득력 있는 추천사를 작성해줘."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7
        )
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "죄송해요, 지금은 추천사를 생성하기 어렵네요. 잠시 후 다시 시도해주세요."