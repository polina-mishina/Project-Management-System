import uuid

from sqlalchemy import Column, Integer, String, Text, UUID, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    project_id = Column(Integer, nullable=False)
    parent_task_id = Column(Integer)
    creator_id = Column(UUID(as_uuid=True), nullable=False)
    executor_id = Column(UUID(as_uuid=True))
    create_date = Column(DateTime(timezone=True))
    update_date = Column(DateTime(timezone=True))
    completion_date = Column(DateTime(timezone=True))
    comments = relationship("Comment", backref='task')


class Comment(Base):
    __tablename__ = "comment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    data = Column(JSONB)
    create_date = Column(DateTime(timezone=True))
    type_id = mapped_column(ForeignKey("comment_type.id"))
    type = relationship("CommentType")
    task_id = mapped_column(ForeignKey("tasks.id", ondelete='CASCADE'))


class CommentType(Base):
    __tablename__ = "comment_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
