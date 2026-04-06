#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EnvVar Service - Business logic for Environment Variable operations.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from models import EnvVar
from schemas import EnvVarCreate, EnvVarUpdate
from repositories import env_var_repo


class EnvVarService:
    """Service layer for EnvVar business logic"""

    def list_env_vars(self, db: Session) -> List[EnvVar]:
        """Get all environment variables"""
        return env_var_repo.get_all(db)

    def get_env_var(self, db: Session, env_id: int) -> Optional[EnvVar]:
        """Get environment variable by ID"""
        return env_var_repo.get_by_id(db, env_id)

    def create_env_var(self, db: Session, env_data: EnvVarCreate) -> EnvVar:
        """Create a new environment variable"""
        if env_var_repo.key_exists(db, env_data.key):
            raise ValueError("Environment variable with this key already exists")

        env_var = EnvVar(
            key=env_data.key,
            value=env_data.value,
            description=env_data.description,
            is_secret=env_data.is_secret,
        )
        db.add(env_var)
        db.commit()
        db.refresh(env_var)
        return env_var

    def update_env_var(self, db: Session, env_id: int, env_data: EnvVarUpdate) -> Optional[EnvVar]:
        """Update an environment variable"""
        env_var = env_var_repo.get_by_id(db, env_id)
        if not env_var:
            return None

        update_dict = env_data.model_dump(exclude_unset=True)

        # Check for key uniqueness if key is being changed
        if "key" in update_dict and update_dict["key"] != env_var.key:
            if env_var_repo.key_exists(db, update_dict["key"], exclude_id=env_id):
                raise ValueError("Environment variable with this key already exists")

        for key, value in update_dict.items():
            if value is not None and hasattr(env_var, key):
                setattr(env_var, key, value)

        db.commit()
        db.refresh(env_var)
        return env_var

    def delete_env_var(self, db: Session, env_id: int) -> bool:
        """Delete an environment variable"""
        return env_var_repo.delete(db, env_id)

    def export_as_dict(self, db: Session) -> Dict[str, str]:
        """Export all env vars as a dictionary for task execution"""
        return env_var_repo.to_dict(db)

    def set_webhook_payload_vars(
        self,
        db: Session,
        payload: Dict[str, any]
    ) -> None:
        """Set environment variables from webhook payload"""
        for key, value in payload.items():
            existing = env_var_repo.get_by_key(db, f"WEBHOOK_PAYLOAD_{key.upper()}")
            if not existing:
                env_var = EnvVar(
                    key=f"WEBHOOK_PAYLOAD_{key.upper()}",
                    value=str(value),
                    description="Webhook payload from trigger"
                )
                db.add(env_var)
        db.commit()


# Singleton instance
env_var_service = EnvVarService()
