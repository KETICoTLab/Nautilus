from fastapi import APIRouter
# from app.routers import (
#     access_policy, country_code, item_code, data_provider, project,
#     job, client, check_status, global_model, performance_history,
#     train_code, service, subscription, preproc_tool, validation_tool
# )
from app.routers import (
    data_provider, project, job, client, result
)

api_router = APIRouter()
# api_router.include_router(access_policy.router)
# api_router.include_router(country_code.router)
# api_router.include_router(item_code.router)
api_router.include_router(data_provider.router)
api_router.include_router(project.router)
api_router.include_router(job.router)
api_router.include_router(client.router)
# api_router.include_router(check_status.router)
# api_router.include_router(global_model.router)
# api_router.include_router(performance_history.router)
# api_router.include_router(train_code.router)
# api_router.include_router(service.router)
# api_router.include_router(subscription.router)
# api_router.include_router(preproc_tool.router)
# api_router.include_router(validation_tool.router)
api_router.include_router(result.router)
