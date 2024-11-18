import datetime
import uuid

from pydantic import BaseModel, ConfigDict


class TaskPydModelInputDTO(BaseModel):
    """DTO for creating new task model."""

    title: str
    description: str


class TaskPydModelUpdateDTO(BaseModel):
    """DTO for updating task model."""

    title: str = None
    description: str = None
    completed: bool = None


class TaskPydModelDTO(TaskPydModelInputDTO):
    """
    DTO for task models.

    It is returned when accessing task models from the API.
    """

    id: uuid.UUID
    completed: bool = False
    created_at: datetime.datetime
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
