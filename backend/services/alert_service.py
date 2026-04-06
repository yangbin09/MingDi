#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alert Service - Business logic for AlertConfig operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from models import AlertConfig
from schemas import AlertConfigCreate, AlertConfigUpdate
from repositories import alert_repo


class AlertService:
    """Service layer for AlertConfig business logic"""

    def list_alerts(self, db: Session) -> List[AlertConfig]:
        """Get all alert configurations"""
        return alert_repo.get_all(db)

    def get_alert(self, db: Session, alert_id: int) -> Optional[AlertConfig]:
        """Get alert configuration by ID"""
        return alert_repo.get_by_id(db, alert_id)

    def create_alert(self, db: Session, alert_data: AlertConfigCreate) -> AlertConfig:
        """Create a new alert configuration"""
        alert = AlertConfig(
            name=alert_data.name,
            webhook_url=alert_data.webhook_url,
            events=alert_data.events,
            is_active=alert_data.is_active,
            ai_humanize=alert_data.ai_humanize,
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    def update_alert(
        self,
        db: Session,
        alert_id: int,
        alert_data: AlertConfigUpdate
    ) -> Optional[AlertConfig]:
        """Update an alert configuration"""
        alert = alert_repo.get_by_id(db, alert_id)
        if not alert:
            return None

        update_dict = alert_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None and hasattr(alert, key):
                setattr(alert, key, value)

        db.commit()
        db.refresh(alert)
        return alert

    def delete_alert(self, db: Session, alert_id: int) -> bool:
        """Delete an alert configuration"""
        return alert_repo.delete(db, alert_id)

    def get_active_alerts(self, db: Session) -> List[AlertConfig]:
        """Get all active alert configurations"""
        return alert_repo.get_active(db)


# Singleton instance
alert_service = AlertService()
