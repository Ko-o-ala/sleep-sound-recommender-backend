# Sleep Sound Recommendation Engine

사용자의 수면 데이터와 설문조사 데이터를 기반으로 맞춤형 수면 사운드를 추천하는 FastAPI 기반 추천 서버입니다.

## 프로젝트 개요

- **목표**: 사용자의 수면 상태, 선호 사운드, 목표 등을 바탕으로 최적의 수면 사운드를 추천
- **기술 스택**: Python, FastAPI, Uvicorn, Pydantic, Sentence-Transformers, FAISS, OpenAI
- **주요 기능**:
  - 설문조사 데이터 기반 추천
  - 수면 데이터 기반 추천
  - 통합 데이터 기반 추천
  
  - RAG(Retrieval-Augmented Generation) 기반 추천 시스템

## 개발 환경 설정 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd python-engine
```

### 2. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
.\venv\Scripts\activate
```

### 3. 의존성 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```bash

MAIN_SERVER_URL=https://kooala.tassoo.uk
MAIN_SERVER_API_KEY=your_api_key_here

# OpenAI API 키
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. 데이터베이스 인덱스 생성
사운드 데이터를 추가/수정한 경우 검색용 인덱스를 새로 생성:

```bash
python3 scripts/index_builder.py
```

### 6. 서버 실행
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

서버가 성공적으로 실행되면 브라우저에서 `http://localhost:8000/docs`로 접속하여 API 문서를 확인할 수 있습니다.

## API 엔드포인트

### 추천 서비스
- **POST** `/recommend` - 설문조사 데이터를 직접 전송하여 추천
- **POST** `/recommend/sleep` - 수면 데이터를 직접 전송하여 추천
- **POST** `/recommend/combined` - 수면 데이터와 설문 데이터를 모두 전송하여 추천



### 시스템
- **GET** `/` - 서버 상태 확인

## 폴더 구조

```
python-engine/
│
├── .env                        # 환경 변수 파일 (Git에서 무시됨)
├── .gitignore
├── app.py                      # FastAPI 서버 진입점
├── README.md
├── requirements.txt
│
├── data/                       # 사운드 데이터 및 인덱스 저장소
│   ├── sound_pool.json        # 사운드 데이터베이스
│   ├── sound_pool_embedded.json
│   └── sound_index.faiss      # FAISS 검색 인덱스
│
├── scripts/                    # 일회성 스크립트
│   ├── embed_generator.py     # 임베딩 생성 스크립트
│   └── index_builder.py       # FAISS 인덱스 빌더
│
├── services/                   # 핵심 비즈니스 로직
│   ├── data_fetcher.py        # 데이터 가져오기 서비스
│   ├── embedding_service.py   # 텍스트 임베딩 서비스
│   ├── llm_service.py         # LLM 연동 서비스
│   ├── rag_recommender.py     # RAG 추천 엔진
│   ├── recommender.py         # 추천 메인 로직
│   └── score_calculator.py    # 점수 계산 로직
│
├── utils/                      # 보조 유틸리티
│   └── prompt_builder.py      # 프롬프트 생성 유틸리티
│
└── venv/                       # 파이썬 가상환경 폴더 (Git에서 무시됨)
```

## API 사용 예시

### 1. 설문 데이터 기반 추천

```bash
POST /recommend

{
  "sleepLightUsage": "moodLight",
  "lightColorTemperature": "warmYellow",
  "noisePreference": "nature",
  "preferredSleepSound": "nature",
  "calmingSoundType": "rain",
  "stressLevel": "high",
  "sleepGoal": "improveSleepQuality"
}
```

### 2. 수면 데이터 기반 추천

```bash
POST /recommend/sleep

{
  "userId": "user123",
  "preferenceMode": "effectiveness",
  "preferredSounds": ["NATURE_1_WATER.mp3"],
  "previous": {
    "sleepScore": 68,
    "deepSleepRatio": 0.12,
    "remSleepRatio": 0.14,
    "awakeRatio": 0.18
  },
  "current": {
    "sleepScore": 75,
    "deepSleepRatio": 0.17,
    "remSleepRatio": 0.19,
    "awakeRatio": 0.13
  },
  "previousRecommendations": ["ASMR_2_HAIR.mp3", "FIRE_2.mp3"]
}
```

### 3. 통합 추천

```bash
POST /recommend/combined

{
  "userId": "user123",
  "preferenceMode": "effectiveness",
  "preferredSounds": ["NATURE_1_WATER.mp3"],
  "previous": {...},
  "current": {...},
  "previousRecommendations": [...],
  "sleepLightUsage": "moodLight",
  "noisePreference": "nature",
  "preferredSleepSound": "nature",
  "stressLevel": "high",
  "sleepGoal": "improveSleepQuality"
}
```

### 응답 예시

```json
{
  "recommendation_text": "당신의 수면 패턴을 분석한 결과, 깊은 수면이 부족한 것으로 보입니다. 이런 경우에는 마음을 차분하게 가라앉혀주는 자연의 소리가 도움이 될 수 있어요. 특히 '여름밤 귀뚜라미 소리'는 복잡한 생각을 잊고 편안하게 잠드는 데 좋은 친구가 되어줄 거예요.",
  "recommended_sounds": [
    {
      "filename": "NATURE_1_WATER.mp3",
      "rank": 1,
      "preference": "none"
    },
    {
      "filename": "ASMR_2_HAIR.mp3", 
      "rank": 2,
      "preference": "top"
    }
  ]
}
```

## 주요 기능

### 1. RAG 기반 추천 시스템
- 사용자 입력을 자연어로 변환
- Sentence-Transformers를 사용한 벡터 임베딩
- FAISS를 통한 유사도 기반 검색
- OpenAI를 사용한 개인화된 추천 텍스트 생성



### 3. 다양한 추천 모드
- **preference**: 사용자 선호도 기반 추천
- **effectiveness**: 수면 개선 효과 기반 추천

### 4. 에러 처리 및 로깅
- 네트워크 오류 처리
- API 키 인증 실패 처리
- 상세한 로깅으로 디버깅 지원

## 환경 변수

| 변수명 | 설명 | 필수 여부 |
|--------|------|-----------|
| `OPENAI_API_KEY` | OpenAI API 키 | 필수 |

## 개발 참고사항

- 모든 API 엔드포인트는 Swagger UI에서 테스트 가능
- 비동기 처리로 성능 최적화
- RAG 기반 추천 시스템으로 개인화된 결과 제공