TABLE_NAME = "projects"

CREATE_TABLE_QUERY = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    project_id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    description TEXT,
    tags TEXT[],
    creator_id TEXT,
    data_provider_ids text[], 
    number_of_clients INT,
    number_of_jobs INT,
    number_of_subscriptions INT,
    project_image TEXT,
    creation_time timestamp with time zone,
    modification_time timestamp with time zone
);
"""
