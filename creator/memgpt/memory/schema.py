import uuid
import datetime

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, DateTime, JSON


Base = declarative_base()


class MemoryMessage(Base):
    __tablename__ = "memory_messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(Text)
    type = Column(Text)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    additional_kwargs = Column(JSON)


class SessionConfig(Base):
    __tablename__ = "session_configs"

    id = Column(Integer, primary_key=True)
    session_id = Column(Text, default=lambda: str(uuid.uuid4()))
    title = Column(Text, default="Untitled")
    created_at = Column(DateTime, default=datetime.datetime.now)
    model_name = Column(Text, default="gpt-4")
    persona = Column(Text)
    human = Column(Text)
    persona_char_limit = Column(Integer, default=2000)
    human_char_limit = Column(Integer, default=2000)
    page_size = Column(Integer, default=5)
