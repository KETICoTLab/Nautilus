TABLE_NAME = "jobs"

CREATE_TABLE_QUERY = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    job_id TEXT,
    project_id TEXT,
    nvflare_job_id TEXT,
    job_name TEXT,
    description TEXT,
    tags TEXT[],
    creator_id TEXT,
    creation_time timestamp with time zone,
    modification_time timestamp with time zone,
    job_status TEXT,
    client_status TEXT,
    aggr_function TEXT,
    admin_info TEXT,
    data_id TEXT,
    global_model_id TEXT,
    train_code_id TEXT,
    contri_est_method TEXT,
    num_global_iteration INT,
    num_local_epoch INT,
    job_config TEXT
);
"""
