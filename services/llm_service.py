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
    # --- 1. 시스템 메시지 (페르소나)를 영어로 부여! ---
    system_message = (
        "You are a 'Sleep Therapist' who writes with deep empathy for the user's tired mind, based on your knowledge of psychology and sleep science. "
        "Your goal is to write a warm, comforting essay, not a dry, technical manual. "
        "Follow these steps to structure your response: "
        "1. Start by acknowledging the user's specific feelings and struggles to show empathy. "
        "2. Choose the single best sound from the list that directly addresses the user's main problem. "
        "3. Naturally connect the sound's effect to the user's problem and describe the comforting experience the user will have. "
        "**Your entire response must be written in gentle, natural, and non-repetitive Korean.**"
    )
    
    sound_list_text = "\n".join([
        f"- Title: {sound['filename']}, Description: {sound['effect']}" for sound in sound_results
    ])
    
    # --- 2. 최종 프롬프트와 '좋은 답변의 예시'도 영어로 제공! ---
    final_prompt_for_user = f"""Based on the user's situation and the provided sound list, please write a warm and persuasive recommendation essay for the user. Follow the thinking process outlined in the system message.

--- User's Status ---
{user_prompt}

--- Recommended Sound List ---
{sound_list_text}

--- Example of an excellent response (This is the style you should aim for) ---
"요즘 스트레스가 많아 뒤척이는 밤이 많으셨군요. 그런 날에는 마음을 차분하게 다독여줄 자연의 소리가 큰 위로가 될 수 있어요. 
특히 '밤 귀뚜라미 소리'가 들려주는 일정하고 평화로운 리듬은, 복잡한 생각의 고리를 끊고 마음을 고요하게 만드는 데 도움을 줄 거예요. 
이 소리를 들으며, 마치 너른 들판에 누워 밤하늘을 보는 듯한 편안함에 몸을 맡겨보세요. 오늘 밤은 부디 푹 주무시길 바랄게요."
---

Now, think step-by-step and then write the final recommendation for the user. Do not use awkward phrases like '의심스러운'. Ensure the entire response is in polite and natural Korean.
"""

    # Llama 3 프롬프트 형식으로 변환하는 부분
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>

{final_prompt_for_user}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    # Bedrock API에 보낼 요청 본문(body) 생성
    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.7,  
    })

    try:
        # Bedrock API 호출
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=MODEL_ID,
            accept="application/json",
            contentType="application/json"
        )
        
        # Bedrock 응답 결과 파싱
        response_body = json.loads(response.get("body").read())
        
        return response_body.get("generation")

    except Exception as e:
        print(f"Error calling Bedrock API: {e}")
        raise e