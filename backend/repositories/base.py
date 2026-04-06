#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Repository - Generic CRUD operations for all entities.
"""
from typing import TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session

from models import Base

T = TypeVar('T', bound=Base)


class BaseRepository:
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        """Fetch entity by primary key"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session) -> List[T]:
        """Fetch all entities"""
        return db.query(self.model).all()

    def get_by_ids(self, db: Session, ids: List[int]) -> Dict[int, T]:
        """Bulk fetch by IDs, returns dict for O(1) lookup"""
        if not ids:
            return {}
        entities = db.query(self.model).filter(self.model.id.in_(ids)).all()
        return {e.id: e for e in entities}

    def delete(self, db: Session, id: int) -> bool:
        """Delete entity by ID, returns True if deleted"""
        obj = self.get_by_id(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def update(self, db: Session, id: int, **kwargs: Any) -> Optional[T]:
        """Update entity fields, returns updated entity"""
        obj = self.get_by_id(db, id)
        if not obj:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    def exists(self, db: Session, id: int) -> bool:
        """Check if entity exists by ID"""
        return db.query(self.model).filter(self.model.id == id).first() is not None

    def count(self, db: Session) -> int:
        """Count total entities"""
        return db.query(self.model).count()
