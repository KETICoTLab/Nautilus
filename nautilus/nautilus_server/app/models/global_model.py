TABLE_NAME = "global_models"

CREATE_TABLE_QUERY = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    global_model_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
    parent_model_id INT,
    global_model_name VARCHAR(255) NOT NULL,
    final_performance_factor NUMERIC NOT NULL,
    train_start_time TIMESTAMP NOT NULL,
    train_end_time TIMESTAMP NOT NULL,
    model_file BYTEA NOT NULL
);
"""
