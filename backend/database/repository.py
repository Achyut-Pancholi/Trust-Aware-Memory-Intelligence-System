from sqlalchemy.orm import Session
from backend.database.models import MemoryEntry, ChangeLog, MemoryStatus
from typing import List, Optional

def get_memory_entry_by_id(db: Session, memory_id: str) -> Optional[MemoryEntry]:
    return db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()

def get_memory_entries_by_subject_predicate(db: Session, subject: str, predicate: str) -> List[MemoryEntry]:
    return db.query(MemoryEntry).filter(
        MemoryEntry.subject == subject,
        MemoryEntry.predicate == predicate
    ).all()

def get_all_memory_entries(db: Session, skip: int = 0, limit: int = 100) -> List[MemoryEntry]:
    return db.query(MemoryEntry).offset(skip).limit(limit).all()

def get_changelogs_for_memory(db: Session, memory_id: str) -> List[ChangeLog]:
    return db.query(ChangeLog).filter(ChangeLog.memory_id == memory_id).order_by(ChangeLog.timestamp.desc()).all()

def get_all_changelogs(db: Session, skip: int = 0, limit: int = 100) -> List[ChangeLog]:
    return db.query(ChangeLog).order_by(ChangeLog.timestamp.desc()).offset(skip).limit(limit).all()

def get_dashboard_stats(db: Session) -> dict:
    from backend.database.models import ActionType
    
    total_memories = db.query(MemoryEntry).count()
    active_memories = db.query(MemoryEntry).filter(MemoryEntry.status == MemoryStatus.ACTIVE).count()
    low_confidence_memories = db.query(MemoryEntry).filter(MemoryEntry.status == MemoryStatus.LOW_CONFIDENCE).count()
    forgotten_memories = db.query(MemoryEntry).filter(MemoryEntry.status == MemoryStatus.FORGOTTEN).count()
    total_claims = db.query(ChangeLog).count()
    
    # Count actions from changelog (more accurate for rejected since no memory entry is created)
    accepted_count = db.query(ChangeLog).filter(ChangeLog.action == ActionType.ACCEPTED).count()
    updated_count = db.query(ChangeLog).filter(ChangeLog.action == ActionType.UPDATED).count()
    rejected_count = db.query(ChangeLog).filter(ChangeLog.action == ActionType.REJECTED).count()
    downgraded_count = db.query(ChangeLog).filter(ChangeLog.action == ActionType.DOWNGRADED).count()
    forgotten_count = db.query(ChangeLog).filter(ChangeLog.action == ActionType.FORGOTTEN).count()
    merged_count = db.query(ChangeLog).filter(ChangeLog.action == ActionType.MERGED).count()
    
    return {
        "total_claims": total_claims,
        "total_memories": total_memories,
        "active_memories": active_memories,
        "low_confidence_memories": low_confidence_memories,
        "forgotten_memories": forgotten_memories,
        "accepted_count": accepted_count,
        "updated_count": updated_count,
        "rejected_count": rejected_count,
        "downgraded_count": downgraded_count,
        "forgotten_count": forgotten_count,
        "merged_count": merged_count,
    }

def clear_database(db: Session):
    db.query(ChangeLog).delete()
    db.query(MemoryEntry).delete()
    db.commit()

