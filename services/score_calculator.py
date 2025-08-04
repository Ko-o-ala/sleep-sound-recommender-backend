# score_calculator.py

import numpy as np

# 사용자의 사운드 선호 순위를 기반으로 softmax 가중치를 계산하는 함수 (filename 기준)
def softmax_rank_weights(preferred_filenames):
    n = len(preferred_filenames)
    ranks = np.arange(n)[::-1]  # 높은 순위일수록 큰 점수 부여
    weights = np.exp(ranks) / np.sum(np.exp(ranks))  # softmax 계산
    return dict(zip(preferred_filenames, weights))  # 사운드 filename별 가중치 딕셔너리 반환


# 이전 수면 점수 대비 현재 점수의 변화량을 바탕으로 효과성 가중치 계산 (filename 기준)
def compute_effectiveness(prev_score, curr_score, main_sounds=[], sub_sounds=[]):
    delta = (curr_score - prev_score) / 100  # 점수 차이 정규화
    eff_dict = {}

    for fname in main_sounds:
        eff_dict[fname] = delta  # 메인 추천은 1.0배
    for fname in sub_sounds:
        eff_dict[fname] = delta * 0.7  # 서브 추천은 0.7배

    return eff_dict  # 사운드 filename별 효과성 가중치 딕셔너리


# 추천 모드에 따라 alpha(선호도), beta(효과성) 가중치 설정
def choose_weights(mode, balance=None):
    if balance is not None:
        # balance: 0~10 정수를 0.0~1.0 실수로 변환
        # 0(선호도 중심) ~ 10(효과성 중심) -> 0.0(선호도 중심) ~ 1.0(효과성 중심)
        normalized_balance = balance / 10.0
        
        # normalized_balance: 0.0(선호도 중심) ~ 1.0(효과성 중심)
        alpha = (1.0 - normalized_balance) * 0.5  # 선호도 가중치 (0.5 ~ 0.0)
        beta = normalized_balance * 0.5  # 효과성 가중치 (0.0 ~ 0.5)
        return alpha, beta
    
    # 기존 모드 호환성 유지
    if mode == "preference":
        return 0.4, 0.1  # 선호도 중심
    elif mode == "effectiveness":
        return 0.1, 0.4  # 수면 개선 중심
    return 0.25, 0.25  # 기본값: 균형형


# 후보 사운드 리스트에 대해 최종 점수 계산 후 정렬하는 메인 함수
def compute_final_scores(candidates, preferred_ids, effectiveness_input, mode="effectiveness", balance=None):
    print("[compute_final_scores] candidates (top 3):", [c.get('filename') for c in candidates[:3]])
    alpha, beta = choose_weights(mode, balance)
    print(f"[compute_final_scores] alpha: {alpha}, beta: {beta}")
    pref_weights = softmax_rank_weights(preferred_ids)
    print("[compute_final_scores] pref_weights:", pref_weights)
    eff_weights = compute_effectiveness(**effectiveness_input)
    print("[compute_final_scores] eff_weights:", eff_weights)
    scored = []
    for sound in candidates:
        sid = sound["filename"]
        base = sound.get("similarity_score", 0)
        pref = pref_weights.get(sid, 0)
        eff = eff_weights.get(sid, 0)
        score = base + alpha * pref + beta * eff
        print(f"[compute_final_scores] sound: {sid}, base: {base}, pref: {pref}, eff: {eff}, score: {score}")
        scored.append({
            "sound": sound,
            "score": score,
            "id": sid,
            "components": {
                "similarity": base,
                "preference": pref,
                "effectiveness": eff
            }
        })
    print("[compute_final_scores] scored (top 3):", [{"filename": s["sound"].get("filename"), "score": s["score"]} for s in scored[:3]])
    return sorted(scored, key=lambda x: x["score"], reverse=True)