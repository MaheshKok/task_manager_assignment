import uuid
from typing import List

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from task_manager.db.dependencies import get_db_session
from task_manager.db.models.task_model import TaskDBModel


class TaskDAO:
    """Class for accessing task table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def create_task(
        self,
        title: str,
        description: str,
        user_id: uuid.UUID,
    ) -> TaskDBModel:
        """
        Add single task to session.

        Args:
            user_id: ID of the user.
            title: title of the task.
            description: description of the task.

        Returns:
            None
        """
        task_db_model = TaskDBModel(
            title=title,
            description=description,
            user_id=user_id,
        )
        self.session.add(task_db_model)
        await self.session.commit()
        await self.session.refresh(task_db_model)
        return task_db_model

    async def get_all_tasks(
        self,
        user_id: uuid.UUID,
        limit: int = 10,
        page: int = 1,
        completed: bool | None = None,
    ) -> List[TaskDBModel]:
        """
        Get all task models with limit/page pagination.

        Args:
            user_id (uuid): ID of the user.
            completed (bool): Filter tasks based on completion status.
            limit (int): Limit of tasks.
            page (int): page of tasks.

        Returns:
            List[TaskDBModel]: Stream of tasks.
        """

        query = select(TaskDBModel).filter_by(user_id=user_id)
        if completed is not None:
            query = query.filter_by(completed=completed)

        offset = (page - 1) * limit
        raw_tasks = await self.session.execute(
            query.limit(limit).offset(offset),
        )
        return list(raw_tasks.scalars().fetchall())

    async def get_task_by_id(
        self,
        user_id: uuid.UUID,
        task_id: uuid.UUID,
    ) -> TaskDBModel | None:
        """
        Get task by id.

        Args:
            user_id (uuid): ID of the user.
            task_id (str): ID of the task.

        Returns:
            TaskDBModel: Task if found, else None.
        """

        raw_task = await self.session.execute(
            select(TaskDBModel).where(
                TaskDBModel.id == task_id,
                TaskDBModel.user_id == user_id,
            ),
        )
        return raw_task.scalar_one_or_none()

    async def update_task(
        self,
        task_db_model: TaskDBModel,
        title: str | None = None,
        description: str | None = None,
        completed: bool | None = None,
    ) -> TaskDBModel:
        """
        Update task details.

        Args:
            task_db_model (TaskDBModel): Task to be updated.
            title (str): New title of the task.
            description (str): New description of the task.
            completed (bool): New completion status of the task.

        Returns:
            TaskDBModel | None: Updated task if found, else None.
        """

        if title:
            task_db_model.title = title

        if description:
            task_db_model.description = description

        if completed is not None:
            task_db_model.completed = completed

        await self.session.commit()
        await self.session.refresh(task_db_model)  # Update the task in the session
        return task_db_model

    async def delete_task(self, task_db_model: TaskDBModel) -> None:
        """
        Delete task by id.

        Args:
            task_db_model: Task to be deleted.

        Returns:
            None

        """

        await self.session.delete(task_db_model)
        await self.session.commit()
