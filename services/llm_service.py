import boto3
import json
from typing import List, Dict

# 1. Bedrock 클라이언트 생성 (AWS CLI 설정 덕분에 키 정보 필요 없음!)
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"  # 반드시 팀에서 사용하는 리전으로 설정!
)

# 2. 사용할 Llama 3 모델 ID 지정
MODEL_ID = "meta.llama3-8b-instruct-v1:0"

# 비동기 처리는 일단 빼고 동기 버전으로 다시 작성 (boto3는 비동기 설정이 더 복잡해서)
def generate_recommendation_text(user_prompt: str, sound_results: List[Dict]) -> str:
    system_message = (
        "너는 사용자의 현재 상황과 기분에 공감하며, 가장 적절한 수면 사운드를 다정하게 추천해주는 전문가야. "
        "주어진 사운드 목록 중에서 가장 적합한 1~2개를 골라, 왜 그 사운드가 사용자에게 도움이 될지 구체적인 이유를 들어 설명해줘."
    )
    sound_list_text = "\n".join([
        f"- 제목: {sound['filename']}, 설명: {sound['effect']}" for sound in sound_results
    ])
    final_prompt_for_user = (
        f"아래는 사용자의 현재 상태와, 그에 맞춰 1차로 추천된 사운드 목록이야.\n\n"
        f"--- 사용자 상태 ---\n{user_prompt}\n\n"
        f"--- 추천 사운드 목록 ---\n{sound_list_text}\n\n"
        f"이 정보를 바탕으로, 사용자만을 위한 따뜻하고 설득력 있는 추천사를 작성해줘."
    )

    # 3. Llama 3가 요구하는 엄격한 프롬프트 형식으로 변환
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

{final_prompt_for_user}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    # 4. Bedrock API에 보낼 요청 본문(body) 생성
    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
    })

    try:
        # 5. Bedrock API 호출
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=MODEL_ID,
            accept="application/json",
            contentType="application/json"
        )
        
        # 6. Bedrock 응답 결과 파싱
        response_body = json.loads(response.get("body").read())
        
        return response_body.get("generation")

    except Exception as e:
        print(f"Error calling Bedrock API: {e}")
        # (fallback 로직은 그대로)
        raise e