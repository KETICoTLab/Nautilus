# Nautilus Federated Learning Platform (FastAPI + PostgreSQL)

## 📌 프로젝트 개요
Nautilus 프로젝트는 **연합 학습(Federated Learning)**을 지원하는 플랫폼으로, **FastAPI + PostgreSQL**을 활용하여 설계되었습니다.

### 🎯 주요 기능
- **Data Provider 관리**: 학습 데이터 제공자 관리
- **Project 관리**: 프로젝트 및 관련 Job 관리
- **Job 관리**: 모델 학습 및 상태 관리
- **Client 관리**: 연합 학습을 위한 클라이언트 관리
- **Global Model 관리**: 학습된 글로벌 모델 저장
- **Performance History 관리**: 모델 성능 이력 관리
- **Service 관리**: 제공 서비스 설정 및 실행
- **Subscription 관리**: 알림 및 구독 기능
- **Validation 및 Preprocessing Tool 지원**: 데이터 전처리 및 검증 기능

---

## 🚀 설치 및 실행 방법

### 1️⃣ **의존성 설치**
```sh
pip install -r requirements.txt
```

### 2️⃣ **PostgreSQL 설정**
PostgreSQL 데이터베이스를 생성하고 config 환경변수에서 `DATABASE_URL`을 설정하세요.
```sh
export DATABASE_URL="postgresql://user:password@localhost:5432/nautilus_db"
```

### 3️⃣ **FastAPI 서버 실행**
```sh
uvicorn app.main:app --reload
```

### 4️⃣ **API 문서 확인**
FastAPI는 자동으로 **Swagger UI** 및 **Redoc** 문서를 생성합니다:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 🏗 디렉토리 구조
nautilus/
├── app/
│   ├── main.py              # FastAPI 실행 파일
│   ├── config.py            # 환경설정 (DB URL, HOST, PORT)
│   ├── database.py          # PostgreSQL 커넥션 풀 생성
│   ├── models/              # 데이터베이스 테이블 정의
│   ├── schemas/             # Pydantic 데이터 검증 모델
│   ├── service/             # 비즈니스 로직 (CRUD 포함)
│   ├── routers/             # API 엔드포인트 정의
├── README.md                # 프로젝트 설명 파일
├── requirements.txt         # 의존성 목록

### 📜 API 엔드포인트 목록
🗂 Data Provider
POST /base/data-providers - 데이터 제공자 등록
GET /base/data-providers/{data_provider_id} - 데이터 제공자 조회
PATCH /base/data-providers/{data_provider_id} - 데이터 제공자 수정
DELETE /base/data-providers/{data_provider_id} - 데이터 제공자 삭제
GET /base/data-providers - 모든 데이터 제공자 조회

🏗 Project
POST /base/projects - 프로젝트 생성
GET /base/projects/{project_id} - 프로젝트 조회
PATCH /base/projects/{project_id} - 프로젝트 수정
DELETE /base/projects/{project_id} - 프로젝트 삭제
GET /base/projects - 모든 프로젝트 조회

🏃 Job
POST /base/projects/{project_id}/jobs - Job 생성
GET /base/projects/{project_id}/jobs/{job_id} - Job 조회
PATCH /base/projects/{project_id}/jobs/{job_id} - Job 수정
DELETE /base/projects/{project_id}/jobs/{job_id} - Job 삭제
GET /base/projects/{project_id}/jobs - 모든 Job 조회

👥 Client
POST /base/projects/{project_id}/clients - Client 등록
GET /base/projects/{project_id}/clients/{client_id} - Client 조회
PATCH /base/projects/{project_id}/clients/{client_id} - Client 수정
DELETE /base/projects/{project_id}/clients/{client_id} - Client 삭제
GET /base/projects/{project_id}/clients - 모든 Client 조회
(나머지 엔드포인트는 routers/ 폴더의 개별 파일 참고)

🛠 기술 스택
백엔드: FastAPI
데이터베이스: PostgreSQL + asyncpg
배포: Uvicorn
