#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Service - Business logic for system-level operations.
Includes system settings and AI configuration.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from repositories import system_settings_repo, env_var_repo


class SystemService:
    """Service layer for system-level business logic"""

    def get_setting(self, db: Session, key: str) -> Optional[str]:
        """Get a system setting value"""
        return system_settings_repo.get_value(db, key)

    def set_setting(
        self,
        db: Session,
        key: str,
        value: str,
        description: Optional[str] = None
    ) -> None:
        """Set a system setting value"""
        system_settings_repo.set_value(db, key, value, description)

    def get_system_settings(self, db: Session) -> Dict[str, Any]:
        """Get all system settings as a structured response"""
        minimax_api_key = system_settings_repo.get_value(db, "minimax_api_key")
        minimax_group_id = system_settings_repo.get_value(db, "minimax_group_id")

        return {
            "minimax_api_key": minimax_api_key,
            "minimax_group_id": minimax_group_id,
            "ai_enabled": bool(minimax_api_key and minimax_group_id)
        }

    def update_system_settings(
        self,
        db: Session,
        minimax_api_key: Optional[str] = None,
        minimax_group_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update system settings"""
        if minimax_api_key is not None:
            system_settings_repo.set_value(
                db, "minimax_api_key", minimax_api_key,
                "Minimax API Key for AI features"
            )
        if minimax_group_id is not None:
            system_settings_repo.set_value(
                db, "minimax_group_id", minimax_group_id,
                "Minimax Group ID for AI features"
            )

        return self.get_system_settings(db)

    def get_env_vars_for_task(self, db: Session) -> Dict[str, str]:
        """Get environment variables for task execution"""
        return env_var_repo.to_dict(db)


# Singleton instance
system_service = SystemService()
