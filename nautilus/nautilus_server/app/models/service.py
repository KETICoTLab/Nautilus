TABLE_NAME = "services"

CREATE_TABLE_QUERY = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    service_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    service_name VARCHAR(255) NOT NULL,
    description TEXT,
    tags TEXT[],
    creator_id INT,
    creation_time TIMESTAMP DEFAULT NOW(),
    modification_time TIMESTAMP DEFAULT NOW(),
    global_model_id INT,
    authorization TEXT,
    service_request_param JSONB,
    service_response_info JSONB,
    response_format_type TEXT,
    interface_type TEXT,
    error_info TEXT
);
"""
