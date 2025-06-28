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
def generate_recommendation_text(user_prompt: str, sound_results: List[Dict], user_preferences: Dict) -> str:
    system_message = (
        "You are a 'Sleep Therapist' who writes with deep empathy, like writing a warm, comforting essay for a close friend. "
        "Your primary goal is to make the user feel understood and cared for. "
        "You will be given a user's needs, their preferences, and a list of recommended sounds. "
        "You must follow the provided reasoning steps precisely to write the final response in gentle, natural Korean."
        "A very important rule: You must NEVER use the Korean word '소음' (noise). Instead, always use '사운드' (sound) or '소리' (sori)."
    )
    
    sound_list_text = "\n".join([
        f"- Title: {sound['title']}, Description: {sound['effect']}" for sound in sound_results
    ])
    
    # --- [최종 진화] LLM에게 '판단 규칙(Rules)'을 명시적으로 부여! ---
    final_prompt_for_user = f"""First, think step-by-step by following these rules, and then write the final recommendation essay for the user.

--- Your Reasoning Steps & Rules ---
1.  Look at the `User's Stated Preference` and the `Top 3 Sounds list`.
2.  **IF** a sound in the Top 3 list matches the user's preference category (e.g., user prefers 'nature' and a nature sound is in the list):
    - **THEN** you MUST prioritize recommending that sound. Start your essay by acknowledging both the preference and the current need, like: "평소에 좋아하시는 OOO 소리가 마침 지금 상황에도 꼭 맞네요."
3.  **IF** none of the Top 3 sounds match the user's preference category:
    - **THEN** you must first acknowledge their preference, and then gently suggest that another sound might be better for their *current* specific need. Start your essay like: "평소 OOO 소리를 즐겨 들으시지만, 오늘은 특별히 이런 문제가 있으니, 가장 유사도가 높은 XXX 소리는 어떠신가요?"
4.  After following these steps, write the final essay based on your conclusion.

--- User's Current Need (deduced from survey) ---
{user_prompt}

--- User's Stated Preference (from survey) ---
The user has explicitly stated they prefer '{user_preferences.get("preferredSleepSound")}' sounds.

--- Top 3 Sounds based on Similarity Search (from RAG) ---
{sound_list_text}
---

**이제, 위의 모든 규칙과 정보를 바탕으로, 최종 추천사를 아주 부드럽고 자연스러운 한국어로 작성해주세요:**
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