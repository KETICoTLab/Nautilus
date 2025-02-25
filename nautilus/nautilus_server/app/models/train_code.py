TABLE_NAME = "train_codes"

CREATE_TABLE_QUERY = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    train_code_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    creator_id INT NOT NULL,
    creation_time TIMESTAMP DEFAULT NOW(),
    modification_time TIMESTAMP DEFAULT NOW(),
    code_file BYTEA NOT NULL
);
"""
