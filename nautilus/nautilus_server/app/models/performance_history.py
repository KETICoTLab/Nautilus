TABLE_NAME = "performance_history"

CREATE_TABLE_QUERY = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    history_data_id SERIAL PRIMARY KEY,
    job_id INT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    global_model_id INT NOT NULL REFERENCES global_models(global_model_id) ON DELETE CASCADE,
    creation_time TIMESTAMP DEFAULT NOW(),
    performance_factor NUMERIC NOT NULL
);
"""
