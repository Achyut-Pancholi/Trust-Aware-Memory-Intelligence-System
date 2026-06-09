from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
import enum
import uuid
import datetime
from backend.database.db import Base

class MemoryStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    OUTDATED = "OUTDATED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    REJECTED = "REJECTED"
    FORGOTTEN = "FORGOTTEN"

class ActionType(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    UPDATED = "UPDATED"
    DOWNGRADED = "DOWNGRADED"
    REJECTED = "REJECTED"
    FORGOTTEN = "FORGOTTEN"
    MERGED = "MERGED"

class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject = Column(String, index=True, nullable=False)
    predicate = Column(String, index=True, nullable=False)
    object = Column(String, nullable=False)
    
    confidence = Column(Float, nullable=False)
    status = Column(Enum(MemoryStatus), default=MemoryStatus.ACTIVE)
    
    sources = Column(JSON, nullable=False, default=list) # List of dictionaries
    
    first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    corroboration_count = Column(Integer, default=1)
    
    # Relationship to changelog
    provenance_history = relationship("ChangeLog", back_populates="memory_entry", cascade="all, delete-orphan")

class ChangeLog(Base):
    __tablename__ = "change_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(String, nullable=False) # ID of the incoming claim
    memory_id = Column(String, ForeignKey("memory_entries.id"), nullable=True)
    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    action = Column(Enum(ActionType), nullable=False)
    reason = Column(Text, nullable=False)
    
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    confidence_delta = Column(Float, default=0.0)

    memory_entry = relationship("MemoryEntry", back_populates="provenance_history")
