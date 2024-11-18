from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from task_manager.db.dependencies import get_db_session
from task_manager.db.models.dummy_model import DummyModel


class DummyDAO:
    """Class for accessing dummy table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def create_dummy_model(self, name: str) -> None:
        """
        Add single dummy to session.

        Args:
            Add single dummy to session.

        """
        self.session.add(DummyModel(name=name))

    async def get_all_dummies(
        self,
        limit: int = 10,
        offset: int = 1,
    ) -> List[DummyModel]:
        """
        Get all dummy models with limit/offset pagination.

        Args:
            limit: limit of dummies.
            offset: offset of dummies.


        Return:
            List of dummy models.
        """
        raw_dummies = await self.session.execute(
            select(DummyModel).limit(limit).offset(offset),
        )

        return list(raw_dummies.scalars().fetchall())

    async def filter(self, name: Optional[str] = None) -> List[DummyModel]:
        """
        Get specific dummy model.

        Args:
            name: name of dummy instance.

        Return:
            List of dummy models.

        """
        query = select(DummyModel)
        if name:
            query = query.where(DummyModel.name == name)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
