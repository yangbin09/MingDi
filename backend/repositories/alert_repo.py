#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alert Repository - Database operations for AlertConfig entity.
"""
from typing import List
from sqlalchemy.orm import Session

from models import AlertConfig
from .base import BaseRepository


class AlertRepository(BaseRepository):
    """Repository for AlertConfig entity"""

    def __init__(self) -> None:
        super().__init__(AlertConfig)

    def get_active(self, db: Session) -> List[AlertConfig]:
        """Get all active alert configurations"""
        return db.query(AlertConfig).filter(AlertConfig.is_active == True)  # noqa: E712.all()


# Singleton instance
alert_repo = AlertRepository()
