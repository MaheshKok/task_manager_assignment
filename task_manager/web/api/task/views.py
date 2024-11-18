import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from starlette import status
from starlette.responses import JSONResponse

from task_manager.db.dao.task_dao import TaskDAO
from task_manager.db.models.users import UserDBModel, current_active_user
from task_manager.web.api.task.schema import (
    TaskPydModelDTO,
    TaskPydModelInputDTO,
    TaskPydModelUpdateDTO,
)

router = APIRouter()


@router.get("/", response_model=List[TaskPydModelDTO])
async def get_task_models(
    limit: int = 10,
    page: int = 1,
    task_dao: TaskDAO = Depends(),
    current_user: UserDBModel = Depends(current_active_user),
    completed: bool | None = None,
) -> List[TaskPydModelDTO]:
    """
    Retrieve all tasks for the current user.

    - **limit**: The maximum number of tasks to return (default is 10).
    - **page**: The page number to retrieve (default is 1).
    - **completed**: Filter tasks based on completion status (`True` or `False`).

    Returns a list of tasks for the authenticated user.
    """

    tasks = await task_dao.get_all_tasks(
        user_id=current_user.id,
        limit=limit,
        page=page,
        completed=completed,
    )
    return [TaskPydModelDTO.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskPydModelDTO)
async def get_task_model_by_id(
    task_id: uuid.UUID,
    task_dao: TaskDAO = Depends(),
    current_user: UserDBModel = Depends(current_active_user),
) -> JSONResponse | TaskPydModelDTO:
    """
    Retrieve a specific task by its ID.

    - **task_id**: The UUID of the task to retrieve.

    Returns the task details if found. Returns a 404 error if the task is not found.
    """

    task_db_model = await task_dao.get_task_by_id(
        task_id=task_id,
        user_id=current_user.id,
    )
    if not task_db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )
    return TaskPydModelDTO.model_validate(task_db_model)


@router.post("/", status_code=201, response_model=TaskPydModelDTO)
async def create_task_model(
    new_task_object: TaskPydModelInputDTO,
    task_dao: TaskDAO = Depends(),
    current_user: UserDBModel = Depends(current_active_user),
) -> TaskPydModelDTO:
    """
    Create a new task.

    - **title**: The title of the task.
    - **description**: A detailed description of the task.

    Returns the newly created task.
    """

    task_db_model = await task_dao.create_task(
        user_id=current_user.id,
        title=new_task_object.title,
        description=new_task_object.description,
    )
    return TaskPydModelDTO.model_validate(task_db_model)


@router.patch("/{task_id}", status_code=200, response_model=Optional[TaskPydModelDTO])
async def update_task_model(
    task_id: uuid.UUID,
    updated_task_object: TaskPydModelUpdateDTO,
    task_dao: TaskDAO = Depends(),
    current_user: UserDBModel = Depends(current_active_user),
) -> JSONResponse | Optional[TaskPydModelDTO]:
    """
    Update an existing task.

    - **task_id**: The UUID of the task to update.
    - **title**: (Optional) The new title of the task.
    - **description**: (Optional) The new description of the task.
    - **completed**: (Optional) The new completion status of the task.

    Returns the updated task. Returns a 404 error if the task is not found.
    """

    task_db_model = await task_dao.get_task_by_id(
        task_id=task_id,
        user_id=current_user.id,
    )
    if not task_db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )
    task_db_model = await task_dao.update_task(
        task_db_model=task_db_model,
        title=updated_task_object.title,
        description=updated_task_object.description,
        completed=updated_task_object.completed,
    )
    return TaskPydModelDTO.model_validate(task_db_model)


@router.delete("/{task_id}", status_code=204)
async def delete_task_model(
    task_id: uuid.UUID,
    task_dao: TaskDAO = Depends(),
    current_user: UserDBModel = Depends(current_active_user),
) -> JSONResponse:
    """
    Delete a task.

    - **task_id**: The UUID of the task to delete.

    Returns a 204 No Content response if the deletion was successful.
    Returns a 404 error if the task is not found.
    """

    task_db_model = await task_dao.get_task_by_id(
        task_id=task_id,
        user_id=current_user.id,
    )
    if not task_db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )
    await task_dao.delete_task(task_db_model=task_db_model)
    return JSONResponse(
        status_code=204,
        content={"message": "Task deleted successfully."},
    )
