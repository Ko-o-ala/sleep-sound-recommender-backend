import boto3
import json
from typing import List, Dict, Union

# Bedrock 클라이언트 초기화
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# Claude 3 Sonnet
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

def generate_recommendation_text(
    user_prompt: Union[str, Dict],
    sound_results: List[Dict],
    user_preferences: Dict
) -> str:
    """
    사용자 상태 설명과 추천 사운드 정보를 바탕으로,
    Claude 3 모델에게 감성적인 한국어 추천 멘트를 요청하고 반환합니다.
    """

    if isinstance(user_prompt, dict):
        user_summary = user_prompt.get("summary", "")
    else:
        user_summary = user_prompt or ""

    # 시스템 지시 메시지 (Claude 3에서는 포함하되 messages에 넣지 않음)
    system_message = (
        "당신은 '수면 테라피스트'입니다. "
        "사용자의 고민과 사운드 정보를 바탕으로, 따뜻하고 감성적인 한국어 추천사를 작성하세요. "
        "설명체가 아닌 감정적이고 부드러운 말투로 작성해주세요. 영어는 절대 사용하지 말고, 반드시 300단어 이상으로 작성하세요."
    )

    sound_list_text = "\n".join([
        f"- 제목: {sound['title']}, 설명: {sound['effect']}" for sound in sound_results
    ])

    example_answer = (
        "예시:\n"
        "요즘 잠이 잘 오지 않아 힘드셨죠?\n"
        "자연의 소리를 좋아하신다고 하셔서, 오늘은 마음을 편안하게 감싸줄 소리들을 준비했어요.\n\n"
        "432Hz 알파파 음악은 조용히 긴장을 풀어주고, 굿나잇 로파이의 잔잔한 리듬은 지친 하루를 천천히 감싸 안아줍니다.\n"
        "계곡물 흐름 소리는 마치 맑은 자연 속에 있는 듯, 당신의 마음을 한결 부드럽게 만들어줄 거예요.\n\n"
        "오늘 밤, 이 소리들과 함께 조용히 숨을 고르며 깊은 쉼을 가져보세요.\n"
        "내일 아침엔 조금 더 가벼운 마음으로 일어나시길 바라요."
    )

    final_prompt_for_user = f"""다음 정보를 참고하여, 따뜻하고 감성적인 수면 추천사를 작성해 주세요.

[1단계] 사용자의 고민에 진심으로 공감하는 문장으로 시작하세요.  
[2단계] 선호하는 사운드를 자연스럽게 언급하며 소개하세요.  
[3단계] 추천 사운드 Top 3를 감성적으로 엮어 연결해 주세요.  
[4단계] 마지막은 위로 또는 희망의 말로 마무리해 주세요.

※ 설명체 말투 대신 감정과 분위기를 표현해 주세요.  
※ “효과가 있습니다”, “추천드립니다”, “사용자님” 등은 사용하지 말아 주세요.  
※ 모든 문장은 부드럽고 따뜻한 일상적 한국어로 구성해 주세요.  
※ 영어는 절대 사용하지 마세요.  
※ 최소 300단어 이상의 부드럽고 감성적인 추천사를 작성해 주세요.  
※ 예시는 참고만 하세요.

--- 사용자 고민 ---
{user_summary}

--- 사용자의 선호 ---
'{user_preferences.get("preferredSleepSound")}' 사운드를 좋아합니다.

--- 추천 사운드 Top 3 ---
{sound_list_text}

{example_answer}
"""

    # Claude용 메시지 형식
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "temperature": 0.7,
        "messages": [
            {"role": "user", "content": f"{system_message}\n\n{final_prompt_for_user}"}
        ]
    })

    try:
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=MODEL_ID,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        return response_body.get("content", [])[0].get("text", "")
    except Exception as e:
        print(f"Error calling Bedrock API: {e}")
        raise e


# --------------------------------------------
# 한글 텍스트 → 영어 번역용 함수 (BGE 임베딩에 쓰임)
# --------------------------------------------
def translate_korean_to_english(text: str) -> str:
    """
    Bedrock LLM을 사용해 주어진 한국어 텍스트를 영어로 번역한다.
    """
    if not text.strip():
        return ""

    prompt = f"""Translate the following Korean text to English. Just give me the translated English words, nothing else.

Korean: "{text}"
English:"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 64,
        "temperature": 0.1,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })

    try:
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=MODEL_ID,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        return response_body.get("content", [])[0].get("text", "").strip()
    except Exception as e:
        print(f"Error during translation: {e}")
        return text
