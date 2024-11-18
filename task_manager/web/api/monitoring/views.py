from fastapi import APIRouter
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/health")
def health_check() -> JSONResponse:
    """
    Checks the health of a project.

    It returns 200 if the project is healthy.
    """

    return JSONResponse(status_code=200, content={"message": "Project is healthy"})
