-- 프로젝트 (projects) 테이블
CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,  -- 프로젝트 ID (문자열, 기본키)
    project_name TEXT,  -- 프로젝트 이름
    description TEXT,  -- 프로젝트 설명 (선택 사항)
    tags TEXT[],  -- 태그 (배열 형태)
    creator_id TEXT,  -- 생성자 ID (정수형)
    data_provider_ids TEXT[],  -- 데이터 제공자 ID 리스트 (배열)
    number_of_clients INTEGER DEFAULT 0,  -- 클라이언트 수 (기본값 0)
    number_of_jobs INTEGER DEFAULT 0,  -- 작업 수 (기본값 0)
    number_of_subscriptions INTEGER DEFAULT 0,  -- 구독 수 (기본값 0)
    project_image TEXT,  -- 프로젝트 이미지 URL (선택 사항)
    creation_time timestamp with time zone,  -- 생성 시간 (기본값 현재 시간)
    modification_time timestamp with time zone  -- 수정 시간 (기본값 현재 시간)
);

-- 데이터 제공자 (Data Providers) 테이블
CREATE TABLE data_providers (
    data_provider_id TEXT PRIMARY KEY,  -- 데이터 제공자 ID
    data_provider_name TEXT,  -- 데이터 제공자 이름 (필수)
    description TEXT,  -- 설명 (선택 사항)
    tags TEXT[],  -- 태그 (배열)
    creator_id TEXT,  -- 생성자 ID (참조 가능)
    host_information JSONB,  -- 호스트 정보 (필수)
    creation_time timestamp with time zone,  -- 생성 시간 (기본값 현재 시간)
    modification_time timestamp with time zone,  -- 수정 시간 (기본값 현재 시간)
    train_code_path TEXT,  -- 학습 코드 경로
    train_data_path TEXT  -- 학습 데이터 경로
);

-- 데이터 (Data) 테이블
CREATE TABLE data (
    data_id TEXT PRIMARY KEY,  -- 데이터 ID
    data_provider_id TEXT,  -- 데이터 제공자 ID (외래키)
    item_code_id TEXT,  -- 아이템 코드 ID
    data_name TEXT,  -- 데이터 이름
    description TEXT,  -- 설명 (선택 사항)
    creation_time timestamp with time zone,  -- 생성 시간 (기본값 현재 시간)
    data TEXT,  -- 실제 데이터 (선택 사항, 바이너리 형태 가능)

    CONSTRAINT fk_data_provider FOREIGN KEY (data_provider_id) REFERENCES data_providers(data_provider_id) ON DELETE CASCADE
);

-- 클라이언트 (Clients) 테이블
CREATE TABLE clients (
    client_id TEXT PRIMARY KEY,  -- 클라이언트 ID
    job_id TEXT,  -- 작업 ID (외래키)
    client_name TEXT,  -- 클라이언트 이름
    data_id TEXT,  -- 데이터 ID (외래키)
    project_id TEXT,
    creation_time timestamp with time zone  -- 생성 시간 (기본값 현재 시간)

);

-- 클라이언트 상태 체크 (Check Status) 테이블
CREATE TABLE check_status (
    check_status_id TEXT PRIMARY KEY,  -- 체크 상태 ID
    client_id TEXT,  -- 클라이언트 ID (외래키)
    job_id TEXT,  -- 작업 ID (외래키)
    validation_status INTEGER NOT NULL DEFAULT -1,  -- 검증 상태 (기본값 FALSE)
    termination_status INTEGER NOT NULL DEFAULT -1,  -- 종료 상태 (기본값 FALSE)
    creation_time timestamp with time zone,  -- 생성 시간 (기본값 현재 시간)

    CONSTRAINT fk_client FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE
);


-- 작업 (Jobs) 테이블
CREATE TABLE jobs (
    job_id TEXT,  -- 작업 ID
    project_id TEXT,  -- 프로젝트 ID (외래키)
    nvflare_job_id TEXT,  -- NVFlare 작업 ID
    job_name TEXT,  -- 작업 이름
    description TEXT,  -- 작업 설명 (선택 사항)
    tags TEXT[],  -- 태그 (배열 형태)
    creator_id TEXT,  -- 작업 생성자 ID
    creation_time timestamp with time zone,  -- 생성 시간
    modification_time timestamp with time zone,  -- 수정 시간
    job_status TEXT,  -- 작업 상태
    client_status TEXT,  -- 클라이언트 상태
    aggr_function TEXT,  -- 집계 함수 (Aggregation Function)
    admin_info TEXT,  -- 관리자 정보
    data_id TEXT,  -- 데이터 ID (외래키)
    global_model_id TEXT,  -- 글로벌 모델 ID (외래키)
    train_code_id TEXT,  -- 학습 코드 ID (외래키)
    contri_est_method TEXT,  -- 기여 추정 방법 (선택 사항)
    num_global_iteration INTEGER,  -- 글로벌 반복 횟수 (선택 사항)
    num_local_epoch INTEGER,  -- 로컬 에폭 횟수 (선택 사항)
    job_config JSON  -- 작업 설정
);

CREATE TABLE results (
    result_id TEXT,
    data JSONB,
    creation_time timestamp with time zone -- 생성 시간
);