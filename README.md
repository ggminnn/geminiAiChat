# ✨ GGM's AI Chat (Streaming & History)
> **FastAPI + Vue 3 + Gemini API를 활용한 컨텍스트 인지형 스트리밍 채팅 앱**

비즈니스 로직과 시스템 아키텍처의 효율성을 고민하며 구축한 프로젝트입니다. 
단순한 채팅을 넘어 대화 히스토리 관리와 AI 응답의 실시간성을 극대화하기 위한 스트리밍 처리에 집중했습니다.

---

## 🛠 Tech Stack

### Backend & AI
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini%202.5-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)

### Frontend
![Vue.js](https://img.shields.io/badge/vue.js-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)

### Database & Environment
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![WSL2](https://img.shields.io/badge/WSL2-0078D4?style=for-the-badge&logo=linux&logoColor=white)

---

## 🎯 Key Features

* **Real-time Streaming**: Gemini API의 스트리밍 응답과 FastAPI의 `StreamingResponse`를 결합하여 답변을 한 글자씩 실시간 렌더링합니다.
* **Conversation History Management**: 
    * **Context Awareness**: 대화 내역을 DB에 영속화하고, 질문 시 이전 문맥을 포함하여 답변의 정확도를 높였습니다.
    * **Efficient Retrieval**: SQLAlchemy를 통해 최근 대화 맥락을 최적화된 로직으로 불러옵니다.
* **Containerized DB**: Docker를 이용해 MySQL 환경을 격리하여 개발 환경의 일관성을 확보했습니다.
* **Modern Architecture**: Backend-Frontend 분리 구조와 CORS 설정을 통한 안정적인 통신 체계를 구축했습니다.

---

## 🏗 System Flow



1. **Client**: Vue 3에서 메시지 입력 및 SSE(Server-Sent Events) 수신 준비
2. **Server**: FastAPI에서 요청 수신 및 DB에서 이전 대화 히스토리 조회
3. **AI**: 최신 대화 맥락을 포함하여 Gemini 모델(2.5+)에 스트리밍 요청
4. **Database**: 새 대화 내용을 SQLAlchemy 세션을 통해 MySQL에 실시간 저장

---

## 🚀 Getting Started

### 1. Prerequisites
* Docker Desktop 실행
* `.env` 파일 생성 후 `GEMINI_API_KEY` 설정

### 2. Backend Setup (WSL2)
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload



---

## 📝 Troubleshooting Log

### 1. WSL2와 Windows Docker MySQL 연동 이슈
- **문제**: WSL2 환경의 FastAPI 서버에서 Windows Docker에 띄운 MySQL로 접속 시 `Connection Refused` 발생.
- **해결**: 
    - `localhost` 바인딩 이슈를 해결하기 위해 Docker 컨테이너 포트 포워딩(3306:3306) 재설정.
    - DB 드라이버를 `mysql-connector-python`으로 교체하여 윈도우-리눅스 간 통신 안정성 확보.

### 2. API 404 NOT_FOUND (Model Naming)
- **문제**: 특정 모델명이 API v1beta 버전에서 인식되지 않아 404 에러 발생.
- **해결**: `client.models.list()`를 통해 현재 API 키로 사용 가능한 정확한 모델 리스트를 조회. 라이브러리 규격에 맞춰 `models/gemini-1.5-flash` 형식으로 수정하여 해결.

### 3. 429 RESOURCE_EXHAUSTED (Quota Issue)
- **문제**: Gemini API 무료 티어 사용 중 요청 횟수 초과로 인한 서비스 중단.
- **해결**: 
    - 429 에러 발생 시 자동 재시도 로직의 필요성 인지.
    - 테스트 가용성 확보를 위해 상황에 따라 모델을 스위칭(1.5 Flash ↔ 2.0/2.5 Flash)하며 개발 흐름 유지.