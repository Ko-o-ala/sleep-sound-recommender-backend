import boto3
import json
from typing import List, Dict

# Bedrock 클라이언트 생성
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

# 사용할 모델 ID
MODEL_ID = "meta.llama3-8b-instruct-v1:0"

def generate_recommendation_text(user_prompt: str, sound_results: List[Dict], user_preferences: Dict) -> str:
    # ✅ System 메시지: 역할, 말투, 금지어 지시 포함
    system_message = (
        "당신은 '수면 테라피스트'입니다.\n"
        "사용자의 고민과 사운드 정보를 바탕으로, 따뜻하고 감성적인 위로가 담긴 한국어 추천사를 작성하세요.\n\n"
        "규칙:\n"
        "- 사용자에게 직접 대화하듯 부드럽고 따뜻하게 말하세요.\n"
        "- '사용자님', '추천드립니다', '도와드리겠습니다' 같은 말투는 사용하지 마세요.\n"
        "- '~효과적입니다', '~효과가 있습니다' 같은 설명식 말투도 피해주세요.\n"
        "- 모든 문장은 부드럽고 감성적인 일상어로 작성하며, 마지막은 위로 또는 희망의 말로 마무리하세요."
    )

    # ✅ 추천 사운드 목록 구성
    sound_list_text = "\n".join([
        f"- 제목: {sound['title']}, 설명: {sound['effect']}" for sound in sound_results
    ])

    # ✅ 감성적 예시 답변
    example_answer = (
        "예시:\n"
        "요즘 잠이 잘 오지 않아 힘드셨죠?\n"
        "자연의 소리를 좋아하신다고 하셔서, 오늘은 마음을 편안하게 감싸줄 소리들을 준비했어요.\n\n"
        "432Hz 알파파 음악은 조용히 긴장을 풀어주고, 굿나잇 로파이의 잔잔한 리듬은 지친 하루를 천천히 감싸 안아줍니다.\n"
        "계곡물 흐름 소리는 마치 맑은 자연 속에 있는 듯, 당신의 마음을 한결 부드럽게 만들어줄 거예요.\n\n"
        "오늘 밤, 이 소리들과 함께 조용히 숨을 고르며 깊은 쉼을 가져보세요.\n"
        "내일 아침엔 조금 더 가벼운 마음으로 일어나시길 바라요."
    )

    # ✅ User Prompt 지시
    final_prompt_for_user = f"""다음 정보를 참고하여, 따뜻하고 감성적인 수면 추천사를 작성해 주세요.

[1단계] 사용자의 고민에 진심으로 공감하는 문장으로 시작하세요.  
[2단계] 선호하는 사운드를 자연스럽게 언급하며 소개하세요.  
[3단계] 추천 사운드 Top 3를 감성적으로 엮어 연결해 주세요.  
[4단계] 마지막은 위로 또는 희망의 말로 마무리해 주세요.

※ 설명체 말투 대신 감정과 분위기를 표현해 주세요.  
※ “효과가 있습니다”, “추천드립니다”, “사용자님” 등은 사용하지 말아 주세요.  
※ 모든 문장은 부드럽고 따뜻한 일상적 한국어로 구성해 주세요.

--- 사용자 고민 ---
{user_prompt}

--- 사용자의 선호 ---
'{user_preferences.get("preferredSleepSound")}' 사운드를 좋아합니다.

--- 추천 사운드 Top 3 ---
{sound_list_text}

{example_answer}
"""

    # ✅ Llama 3 프롬프트 포맷 구성
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>
{final_prompt_for_user}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    # API 요청 본문 구성
    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.7,
    })

    try:
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=MODEL_ID,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        return response_body.get("generation")

    except Exception as e:
        print(f"Error calling Bedrock API: {e}")
        raise e

# input이 한글로 들어온경우 번역해서 돌려주기
def translate_korean_to_english(text: str) -> str:
    """
    Bedrock LLM을 사용해 주어진 한국어 텍스트를 영어로 번역한다.
    """
    if not text.strip(): # 비어있는 텍스트는 번역하지 않음
        return ""

    # 번역을 위한 간단하고 명확한 프롬프트
    prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

Translate the following Korean text to English. Just give me the translated English words, nothing else.
Korean: "{text}"
English:<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 64, # 번역은 길 필요 없으니 짧게
        "temperature": 0.1, # 사실 기반 번역이므로 온도는 낮게
    })

    try:
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=MODEL_ID,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response.get("body").read())
        translated_text = response_body.get("generation").strip()
        print(f"DEBUG: Translated '{text}' -> '{translated_text}'")
        return translated_text
    except Exception as e:
        print(f"Error during translation: {e}")
        return text # 번역 실패 시 원본 텍스트 반환