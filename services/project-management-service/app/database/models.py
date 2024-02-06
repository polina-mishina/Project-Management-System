from sqlalchemy import Column, Integer, String, Text, UUID, DateTime
from .database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text, default='')
    creator_id = Column(UUID(as_uuid=True), nullable=False)
    add_date = Column(DateTime(timezone=True))
    update_date = Column(DateTime(timezone=True))
