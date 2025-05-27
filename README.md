# Sleep Sound Recommendation Engine

수면 개선을 위한 맞춤형 사운드를 추천해주는 FastAPI 기반 추천 서버입니다.  
LLM 기반 사용자 요약 + 벡터 임베딩 + FAISS 유사도 검색을 통해 RAG 구조로 작동하며,  
Bedrock 없이도 로컬에서 전체 파이프라인을 실행할 수 있도록 설계되었습니다.

---

## 프로젝트 개요

- **목표**: 사용자의 수면 상태, 선호 사운드, 목표 등을 바탕으로 최적의 수면 사운드를 추천
- **기술 스택**: Python, FastAPI, FAISS, SentenceTransformer
- **구조 요약**:
  1. 사용자 입력 (JSON) 수신
  2. 자연어 프롬프트로 요약
  3. 임베딩 벡터 생성
  4. FAISS를 통한 유사도 기반 추천
  5. JSON 형태로 추천 결과 반환

---

## 폴더 구조

```
PYTHON-ENGINE/
│
├── app.py                        # FastAPI 서버 진입점
├── requirements.txt
├── README.md
│
├── data/                         # 사운드 데이터 및 임베딩 벡터 저장소
│   ├── sound_pool.json
│   ├── sound_pool_embedding.json
│   └── sound_index.faiss
│
├── scripts/                      # 초기 데이터 임베딩 및 인덱싱
│   ├── embed_generator.py
│   └── index_builder.py
│
├── services/                     # 주요 추천 서비스 로직
│   ├── embedding_service.py
│   ├── rag_recommender.py
│   └── recommender.py
│
├── utils/                        # 프롬프트 생성 유틸
│   └── prompt_builder.py
```

---

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. FAISS 인덱스 생성

```bash
python scripts/index_builder.py
```

### 3. 서버 실행

```bash
uvicorn app:app --reload
```

---

## 테스트 예시 (POST 요청)

### 요청 형식

```json
POST /recommend

{
  "goal": "빠르게 잠들고 싶어요",
  "preference": ["자연", "로파이"],
  "issues": "요즘 스트레스가 많고 뒤척임이 심해요"
}
```

### 응답 예시

```json
{
  "recommendations": [
    {
      "title": "숲속 새소리",
      "category": "자연",
      "description": "잔잔한 새소리가 마음을 편안하게 해줍니다.",
      "audio_url": "https://..."
    }
  ]
}
```