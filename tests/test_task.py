import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from task_manager.db.dao.task_dao import TaskDAO
from task_manager.db.models.users import UserDBModel, current_active_user


@pytest.mark.anyio
async def test_get_tasks_for_single_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    test_user: UserDBModel,
) -> None:
    """Test retrieving tasks for a single user when multiple users exist."""

    # Define the override function
    async def override_current_user() -> UserDBModel:
        return test_user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    # Create a second test user
    second_user = UserDBModel(
        id=uuid.uuid4(),
        email="second_user@example.com",
        hashed_password="fakehashedpassword2",
        is_active=True,
        is_superuser=False,
    )
    dbsession.add(second_user)
    await dbsession.commit()

    # Create tasks for both users
    task_dao = TaskDAO(dbsession)
    await task_dao.create_task(
        title="User1 Task1",
        description="Description for User1 Task1",
        user_id=test_user.id,
    )
    await task_dao.create_task(
        title="User1 Task2",
        description="Description for User1 Task2",
        user_id=test_user.id,
    )
    await task_dao.create_task(
        title="User2 Task1",
        description="Description for User2 Task1",
        user_id=second_user.id,
    )

    # Retrieve tasks for test_user
    url = fastapi_app.url_path_for("get_task_models")
    response = await client.get(url)
    tasks = response.json()

    # Verify that only test_user's tasks are returned
    assert response.status_code == status.HTTP_200_OK
    assert len(tasks) == 2
    titles = [task["title"] for task in tasks]
    assert "User1 Task1" in titles
    assert "User1 Task2" in titles
    assert "User2 Task1" not in titles


@pytest.mark.anyio
async def test_getting_task_by_id(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    test_user: UserDBModel,
) -> None:
    """Tests task instance retrieval."""

    # Define the override function
    async def override_current_user() -> UserDBModel:
        return test_user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    # Create a task
    task_dao = TaskDAO(dbsession)
    task_db_model = await task_dao.create_task(
        title="Test Task 1",
        description="Test Description 1",
        user_id=test_user.id,
    )
    await task_dao.create_task(
        title="Test Task 2",
        description="Test Description 2",
        user_id=test_user.id,
    )
    url = fastapi_app.url_path_for(
        "get_task_model_by_id",
        task_id=str(task_db_model.id),
    )
    # Get tasks with authentication
    response = await client.get(url)
    task = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert task["id"] == str(task_db_model.id)


@pytest.mark.anyio
async def test_get_task_by_id_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    test_user: UserDBModel,
) -> None:
    """Test retrieving a task by ID that doesn't exist."""

    # Define the override function
    async def override_current_user() -> UserDBModel:
        return test_user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    # Attempt to retrieve a non-existent task
    non_existent_task_id = uuid.uuid4()
    url = fastapi_app.url_path_for(
        "get_task_model_by_id",
        task_id=str(non_existent_task_id),
    )
    response = await client.get(url)

    # Verify a 404 Not Found response
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_update_task(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    test_user: UserDBModel,
) -> None:
    """Test updating a task's title, description, and completed status."""

    # Define the override function
    async def override_current_user() -> UserDBModel:
        return test_user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    # Create a task
    task_dao = TaskDAO(dbsession)
    task = await task_dao.create_task(
        title="Original Title",
        description="Original Description",
        user_id=test_user.id,
    )

    # Data to update
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True,
    }

    # Update the task
    url = fastapi_app.url_path_for("update_task_model", task_id=str(task.id))
    response = await client.patch(url, json=update_data)
    updated_task = response.json()

    # Verify the task was updated
    assert response.status_code == status.HTTP_200_OK
    assert updated_task["title"] == "Updated Title"
    assert updated_task["description"] == "Updated Description"
    assert updated_task["completed"] is True


@pytest.mark.anyio
async def test_update_task_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    test_user: UserDBModel,
) -> None:
    """Test updating a task that doesn't exist."""

    # Define the override function
    async def override_current_user() -> UserDBModel:
        return test_user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    # Attempt to update a non-existent task
    non_existent_task_id = uuid.uuid4()
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "completed": True,
    }
    url = fastapi_app.url_path_for(
        "update_task_model",
        task_id=str(non_existent_task_id),
    )
    response = await client.patch(url, json=update_data)

    # Verify a 404 Not Found response
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_delete_task(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    test_user: UserDBModel,
) -> None:
    """Test deleting a task."""

    # Define the override function
    async def override_current_user() -> UserDBModel:
        return test_user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    # Create a task
    task_dao = TaskDAO(dbsession)
    task = await task_dao.create_task(
        title="Task to Delete",
        description="Will be deleted",
        user_id=test_user.id,
    )

    # Delete the task
    url = fastapi_app.url_path_for("delete_task_model", task_id=str(task.id))
    response = await client.delete(url)

    # Verify the task was deleted
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the task no longer exists
    url = fastapi_app.url_path_for("get_task_model_by_id", task_id=str(task.id))
    response = await client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.anyio
async def test_delete_task_not_found(
    fastapi_app: FastAPI,
    client: AsyncClient,
    test_user: UserDBModel,
) -> None:
    """Test deleting a task that doesn't exist."""

    # Define the override function
    async def override_current_user() -> UserDBModel:
        return test_user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    # Attempt to delete a non-existent task
    non_existent_task_id = uuid.uuid4()
    url = fastapi_app.url_path_for(
        "delete_task_model",
        task_id=str(non_existent_task_id),
    )
    response = await client.delete(url)

    # Verify a 404 Not Found response
    assert response.status_code == status.HTTP_404_NOT_FOUND
