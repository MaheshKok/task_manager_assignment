from fastapi import Depends
from fastapi.routing import APIRouter

from task_manager.db.models.users import current_active_user
from task_manager.web.api import (
    docs,
    dummy,
    echo,
    monitoring,
    rabbit,
    redis,
    task,
    users,
)

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(docs.router)
api_router.include_router(
    task.router,
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(current_active_user)],
    responses={404: {"description": "Not Found"}},
)
api_router.include_router(
    dummy.router,
    prefix="/dummy",
    tags=["dummy"],
    responses={404: {"description": "Not Found"}},
)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
api_router.include_router(rabbit.router, prefix="/rabbit", tags=["rabbit"])
