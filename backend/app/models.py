from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    api_key = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    projects = relationship("Project", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String)
    description = Column(String, nullable=True)
    user_id = Column(String, ForeignKey("users.id"))
    style_id = Column(String, ForeignKey("style_profiles.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="projects")
    chapters = relationship("Chapter", back_populates="project")
    characters = relationship("Character", back_populates="project")
    style = relationship("StyleProfile", back_populates="projects")

class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String)
    order = Column(Integer)
    project_id = Column(String, ForeignKey("projects.id"))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="chapters")
    scenes = relationship("Scene", back_populates="chapter")
    pages = relationship("Page", back_populates="chapter")

class Scene(Base):
    __tablename__ = "scenes"
    id = Column(String, primary_key=True, default=generate_uuid)
    order = Column(Integer)
    chapter_id = Column(String, ForeignKey("chapters.id"))
    text = Column(Text)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chapter = relationship("Chapter", back_populates="scenes")
    dialogues = relationship("Dialogue", back_populates="scene")
    panels = relationship("Panel", back_populates="scene")

class Character(Base):
    __tablename__ = "characters"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    description = Column(Text, nullable=True)
    traits = Column(JSON) # List of strings
    project_id = Column(String, ForeignKey("projects.id"))
    visual_ref_url = Column(String, nullable=True)
    lora_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="characters")
    dialogues = relationship("Dialogue", back_populates="character")

class Dialogue(Base):
    __tablename__ = "dialogues"
    id = Column(String, primary_key=True, default=generate_uuid)
    character_id = Column(String, ForeignKey("characters.id"), nullable=True)
    scene_id = Column(String, ForeignKey("scenes.id"))
    text = Column(Text)
    order = Column(Integer)

    character = relationship("Character", back_populates="dialogues")
    scene = relationship("Scene", back_populates="dialogues")

class Page(Base):
    __tablename__ = "pages"
    id = Column(String, primary_key=True, default=generate_uuid)
    order = Column(Integer)
    chapter_id = Column(String, ForeignKey("chapters.id"))
    layout = Column(JSON)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chapter = relationship("Chapter", back_populates="pages")

class Panel(Base):
    __tablename__ = "panels"
    id = Column(String, primary_key=True, default=generate_uuid)
    scene_id = Column(String, ForeignKey("scenes.id"))
    image_url = Column(String)
    prompt = Column(Text)
    style = Column(JSON, nullable=True)

    scene = relationship("Scene", back_populates="panels")

class StyleProfile(Base):
    __tablename__ = "style_profiles"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    source_url = Column(String, nullable=True)
    features = Column(JSON) # Extracted style features

    projects = relationship("Project", back_populates="style")
