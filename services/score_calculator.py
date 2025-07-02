import numpy as np

def softmax_rank_weights(preferred_ids):
    n = len(preferred_ids)
    ranks = np.arrange(n)[::-1] # 높은 순위 → 큰 점수 부여
    weights = np.exp(ranks) / np.sum(np.exp(ranks))
    return dict(zip(preferred_ids, weights))

def compute_effectiveness(prev_score, curr_score, recommended):
    delta = (curr_score - prev_score) / 100
    return {sid: delta * (1 - 0.2 * i) for i, sid in enumerate(recommended)}

def compute_final_scores(candidates, preferred_ids, effectiveness_input, mode="effectiveness"):
    alpha, beta = choose_weights(mode)
    pref_weights = softmax_rank_weights(preferred_ids)
    eff_weights = compute_effectiveness(**effectiveness_input)

    scored = []
    for sound in candidates:
        base = sound["similarity_score"]
        pref = pref_weights.get(sound["id"], 0)
        eff = eff_weights.get(sound["id"], 0)
        score = base + alpha * pref + beta * eff
        scored.append({"sound": sound, "score": score, "id": sound["id"]})

    return sorted(scored, key=lambda x: x["score"], reverse=True)

def choose_weights(mode):
    if mode == "preference":
        return 0.4, 0.1
    elif mode == "effectiveness":
        return 0.1, 0.4
    return 0.25, 0.25