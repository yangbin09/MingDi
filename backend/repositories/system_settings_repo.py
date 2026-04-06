#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SystemSettings Repository - Database operations for SystemSettings entity.
"""
from typing import Optional, Dict
from sqlalchemy.orm import Session

from models import SystemSettings
from .base import BaseRepository


class SystemSettingsRepository(BaseRepository):
    """Repository for SystemSettings entity"""

    def __init__(self) -> None:
        super().__init__(SystemSettings)

    def get_by_key(self, db: Session, key: str) -> Optional[SystemSettings]:
        """Get setting by key"""
        return db.query(SystemSettings).filter(SystemSettings.key == key).first()

    def get_value(self, db: Session, key: str) -> Optional[str]:
        """Get setting value by key"""
        setting = self.get_by_key(db, key)
        return setting.value if setting else None

    def set_value(self, db: Session, key: str, value: str, description: Optional[str] = None) -> None:
        """Set a setting value (upsert)"""
        setting = self.get_by_key(db, key)
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = SystemSettings(key=key, value=value, description=description)
            db.add(setting)
        db.commit()

    def get_all_as_dict(self, db: Session) -> Dict[str, str]:
        """Get all settings as key-value dictionary"""
        settings = self.get_all(db)
        return {s.key: s.value for s in settings if s.value}


# Singleton instance
system_settings_repo = SystemSettingsRepository()
