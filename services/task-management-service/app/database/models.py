from sqlalchemy import Column, Integer, String, Text, UUID, DateTime

from .database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text, default='')
    project_id = Column(Integer, nullable=False)
    parent_task_id = Column(Integer)
    creator_id = Column(UUID(as_uuid=True), nullable=False)
    executor_id = Column(UUID(as_uuid=True))
    add_date = Column(DateTime(timezone=True))
    update_date = Column(DateTime(timezone=True))
