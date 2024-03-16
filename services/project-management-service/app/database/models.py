import uuid

from sqlalchemy import Column, Integer, String, Text, UUID, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    creator_id = Column(UUID(as_uuid=True), nullable=False)
    create_date = Column(DateTime(timezone=True))
    update_date = Column(DateTime(timezone=True))
    completion_date = Column(DateTime(timezone=True))
    comments = relationship("ProjectComment", backref='project')
    documents = relationship("ProjectDocument", backref='project')


class ProjectComment(Base):
    __tablename__ = "project_comment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    data = Column(JSONB)
    create_date = Column(DateTime(timezone=True))
    type_id = mapped_column(ForeignKey("project_comment_type.id"))
    type = relationship("ProjectCommentType")
    project_id = mapped_column(ForeignKey("projects.id", ondelete='CASCADE'), nullable=False)


class ProjectCommentType(Base):
    __tablename__ = "project_comment_type"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class ProjectDocument(Base):
    __tablename__ = "project_document"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    create_date = Column(DateTime(timezone=True))
    project_id = mapped_column(ForeignKey("projects.id", ondelete='CASCADE'), nullable=False)
