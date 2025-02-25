from app.models.access_policy import CREATE_TABLE_QUERY as ACCESS_POLICY
from app.models.country_code import CREATE_TABLE_QUERY as COUNTRY_CODE
from app.models.item_code import CREATE_TABLE_QUERY as ITEM_CODE
from app.models.data_provider import CREATE_TABLE_QUERY as DATA_PROVIDER
from app.models.project import CREATE_TABLE_QUERY as PROJECT
from app.models.job import CREATE_TABLE_QUERY as JOB
from app.models.client import CREATE_TABLE_QUERY as CLIENT
from app.models.check_status import CREATE_TABLE_QUERY as CHECK_STATUS
from app.models.global_model import CREATE_TABLE_QUERY as GLOBAL_MODEL
from app.models.performance_history import CREATE_TABLE_QUERY as PERFORMANCE_HISTORY
from app.models.train_code import CREATE_TABLE_QUERY as TRAIN_CODE
from app.models.service import CREATE_TABLE_QUERY as SERVICE
from app.models.subscription import CREATE_TABLE_QUERY as SUBSCRIPTION
from app.models.preproc_tool import CREATE_TABLE_QUERY as PREPROC_TOOL
from app.models.validation_tool import CREATE_TABLE_QUERY as VALIDATION_TOOL

TABLE_QUERIES = [
    ACCESS_POLICY, COUNTRY_CODE, ITEM_CODE, DATA_PROVIDER,
    PROJECT, JOB, CLIENT, CHECK_STATUS, GLOBAL_MODEL,
    PERFORMANCE_HISTORY, TRAIN_CODE, SERVICE, SUBSCRIPTION,
    PREPROC_TOOL, VALIDATION_TOOL
]
