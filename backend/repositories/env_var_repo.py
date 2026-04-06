#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EnvVar Repository - Database operations for EnvVar entity.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from models import EnvVar
from .base import BaseRepository


class EnvVarRepository(BaseRepository):
    """Repository for EnvVar entity"""

    def __init__(self) -> None:
        super().__init__(EnvVar)

    def get_by_key(self, db: Session, key: str) -> Optional[EnvVar]:
        """Find environment variable by key"""
        return db.query(EnvVar).filter(EnvVar.key == key).first()

    def get_by_keys(self, db: Session, keys: List[str]) -> List[EnvVar]:
        """Find environment variables by keys"""
        return db.query(EnvVar).filter(EnvVar.key.in_(keys)).all()

    def key_exists(self, db: Session, key: str, exclude_id: Optional[int] = None) -> bool:
        """Check if a key already exists"""
        query = db.query(EnvVar).filter(EnvVar.key == key)
        if exclude_id is not None:
            query = query.filter(EnvVar.id != exclude_id)
        return query.first() is not None

    def to_dict(self, db: Session) -> Dict[str, str]:
        """Export all env vars as a dictionary"""
        env_vars = self.get_all(db)
        return {ev.key: ev.value for ev in env_vars}


# Singleton instance
env_var_repo = EnvVarRepository()
