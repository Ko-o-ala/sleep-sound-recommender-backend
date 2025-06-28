# utils/prompt_builder.py

from typing import Dict

def build_prompt(user_input: Dict[str, any]) -> str:
    """
    사용자 입력 JSON을 자연어 프롬프트로 변환함
    실제 연동 시에는 프론트에서 받은 데이터를 기반으로 실행됨
    
    Args:
        user_input (dict): 프론트에서 전달된 사용자 입력

    Returns:
        str: 자연어 형태로 구성된 요약 문장 (프롬프트)
    """
    goal = user_input.get("goal", "편안하게 잠들고 싶어함")
    preference = user_input.get("preference", [])
    issues = user_input.get("issues", "최근 수면의 질이 낮음")

    return (
        f"A user whose goal is '{goal}'. "
        f"Preferred sound categories are {', '.join(preference)}. "
        f"The user's recent issue is '{issues}'."
    )

if __name__ == "__main__":
    # 테스트용 mock 데이터
    mock_input = {
        "goal": "빠르게 잠들고 싶어요",
        "preference": ["자연", "로파이"],
        "issues": "요즘 스트레스가 많고 뒤척임이 심해요"
    }

    prompt = build_prompt(mock_input)
    print("[TEST CASE] 생성된 프롬프트:\n", prompt)