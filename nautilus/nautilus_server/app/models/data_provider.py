
TABLE_NAME = "data_providers"

CREATE_TABLE_QUERY = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    data_provider_id SERIAL PRIMARY KEY,
    data_provider_name VARCHAR(255) NOT NULL,
    description TEXT,
    tags TEXT[],
    creator_id INT,
    host_information TEXT NOT NULL,
    train_code_path TEXT NOT NULL,
    train_data_path TEXT NOT NULL
);
"""
