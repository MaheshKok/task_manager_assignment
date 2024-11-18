import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from task_manager.db.models.users import UserCreate, UserDBModel


class UserDAO:
    """Class for interacting with the 'users' table."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the DAO with the given session.

        Args:
           session (AsyncSession): The database session to use for interacting with the 'users' table.
        """

        self.session = session

    async def create_user(self, user: UserCreate) -> UserDBModel:
        """
        Create a new user in the database.

        Args:
            user (UserCreate): The user to create.

        Returns:
            UserDBModel: The newly created user.
        """

        db_user = UserDBModel(
            email=user.email,
            hashed_password=user.password,  # In real app, hash the password
            is_superuser=user.is_superuser,
            is_active=user.is_active,
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserDBModel | None:
        """
        Get a user by their ID.

        Args:
            user_id (uuid.UUID): The ID of the user to retrieve.

        Returns:
            UserDBModel | None: The user if found, else None.
        """
        query = select(UserDBModel).where(UserDBModel.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
