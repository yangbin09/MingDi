#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Hub Repositories - Database operations for AI-related entities.
Includes: AIProvider, AIModel, AIFeatureRouting, AIPromptTemplate,
AIRAGContext, AIPermissionLevel, AIUsageStats, AIAuditLog
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from models import (
    AIProvider, AIModel, AIFeatureRouting, AIPromptTemplate,
    AIRAGContext, AIPermissionLevel, AIUsageStats, AIAuditLog
)
from .base import BaseRepository


# ============ AI Provider ============

class AIProviderRepository(BaseRepository):
    """Repository for AIProvider entity"""

    def __init__(self) -> None:
        super().__init__(AIProvider)

    def get_ordered(self, db: Session) -> List[AIProvider]:
        """Get all providers ordered by priority"""
        return db.query(AIProvider).order_by(AIProvider.priority).all()

    def get_primary(self, db: Session) -> Optional[AIProvider]:
        """Get the primary provider"""
        return db.query(AIProvider).filter(AIProvider.is_primary == True).first()  # noqa: E712

    def get_enabled(self, db: Session) -> List[AIProvider]:
        """Get all enabled providers"""
        return db.query(AIProvider).filter(AIProvider.is_enabled == True).order_by(AIProvider.priority).all()  # noqa: E712


ai_provider_repo = AIProviderRepository()


# ============ AI Model ============

class AIModelRepository(BaseRepository):
    """Repository for AIModel entity"""

    def __init__(self) -> None:
        super().__init__(AIModel)

    def get_by_provider(self, db: Session, provider_id: int) -> List[AIModel]:
        """Get all models for a provider"""
        return db.query(AIModel).filter(AIModel.provider_id == provider_id).all()

    def get_enabled(self, db: Session) -> List[AIModel]:
        """Get all enabled models"""
        return db.query(AIModel).filter(AIModel.is_enabled == True).all()  # noqa: E712

    def get_by_ids(self, db: Session, model_ids: List[int]) -> List[AIModel]:
        """Get models by IDs"""
        if not model_ids:
            return []
        return db.query(AIModel).filter(AIModel.id.in_(model_ids)).all()


ai_model_repo = AIModelRepository()


# ============ AI Feature Routing ============

class AIFeatureRoutingRepository(BaseRepository):
    """Repository for AIFeatureRouting entity"""

    def __init__(self) -> None:
        super().__init__(AIFeatureRouting)

    def get_by_feature(self, db: Session, feature: str) -> Optional[AIFeatureRouting]:
        """Get routing config by feature name"""
        return db.query(AIFeatureRouting).filter(AIFeatureRouting.feature == feature).first()

    def get_enabled(self, db: Session) -> List[AIFeatureRouting]:
        """Get all enabled routing configs"""
        return db.query(AIFeatureRouting).filter(AIFeatureRouting.is_enabled == True).all()  # noqa: E712


ai_feature_routing_repo = AIFeatureRoutingRepository()


# ============ AI Prompt Template ============

class AIPromptTemplateRepository(BaseRepository):
    """Repository for AIPromptTemplate entity"""

    def __init__(self) -> None:
        super().__init__(AIPromptTemplate)

    def get_by_feature(self, db: Session, feature: str) -> Optional[AIPromptTemplate]:
        """Get template by feature name"""
        return db.query(AIPromptTemplate).filter(AIPromptTemplate.feature == feature).first()

    def get_enabled(self, db: Session) -> List[AIPromptTemplate]:
        """Get all enabled templates"""
        return db.query(AIPromptTemplate).filter(AIPromptTemplate.is_enabled == True).all()  # noqa: E712


ai_prompt_template_repo = AIPromptTemplateRepository()


# ============ AI RAG Context ============

class AIRAGContextRepository(BaseRepository):
    """Repository for AIRAGContext entity"""

    def __init__(self) -> None:
        super().__init__(AIRAGContext)

    def get_by_type(self, db: Session, context_type: str) -> List[AIRAGContext]:
        """Get contexts by type"""
        return db.query(AIRAGContext).filter(
            AIRAGContext.context_type == context_type,
            AIRAGContext.is_enabled == True  # noqa: E712
        ).all()

    def get_enabled(self, db: Session) -> List[AIRAGContext]:
        """Get all enabled contexts"""
        return db.query(AIRAGContext).filter(AIRAGContext.is_enabled == True).all()  # noqa: E712


ai_rag_context_repo = AIRAGContextRepository()


# ============ AI Permission Level ============

class AIPermissionLevelRepository(BaseRepository):
    """Repository for AIPermissionLevel entity"""

    def __init__(self) -> None:
        super().__init__(AIPermissionLevel)

    def get_enabled(self, db: Session) -> List[AIPermissionLevel]:
        """Get all enabled permission levels"""
        return db.query(AIPermissionLevel).filter(AIPermissionLevel.is_enabled == True).all()  # noqa: E712


ai_permission_level_repo = AIPermissionLevelRepository()


# ============ AI Usage Stats ============

class AIUsageStatsRepository(BaseRepository):
    """Repository for AIUsageStats entity"""

    def __init__(self) -> None:
        super().__init__(AIUsageStats)

    def get_by_date(self, db: Session, date: str) -> List[AIUsageStats]:
        """Get stats for a specific date"""
        return db.query(AIUsageStats).filter(AIUsageStats.date == date).all()

    def upsert(
        self,
        db: Session,
        feature: str,
        date: str,
        model_id: Optional[int] = None,
        provider_id: Optional[int] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
        cache_hit: bool = False
    ) -> AIUsageStats:
        """Update or create usage stats for a feature/date/model combination"""
        query = db.query(AIUsageStats).filter(
            AIUsageStats.feature == feature,
            AIUsageStats.date == date,
            AIUsageStats.model_id == model_id,
            AIUsageStats.provider_id == provider_id
        )
        stats = query.first()

        if stats:
            stats.input_tokens += input_tokens
            stats.output_tokens += output_tokens
            stats.total_tokens += input_tokens + output_tokens
            stats.cost_usd += cost_usd
            stats.request_count += 1
            if cache_hit:
                stats.cache_hit_count += 1
        else:
            stats = AIUsageStats(
                feature=feature,
                date=date,
                model_id=model_id,
                provider_id=provider_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost_usd=cost_usd,
                request_count=1,
                cache_hit_count=1 if cache_hit else 0
            )
            db.add(stats)

        db.commit()
        db.refresh(stats)
        return stats


ai_usage_stats_repo = AIUsageStatsRepository()


# ============ AI Audit Log ============

class AIAuditLogRepository(BaseRepository):
    """Repository for AIAuditLog entity"""

    def __init__(self) -> None:
        super().__init__(AIAuditLog)

    def create(
        self,
        db: Session,
        feature: str,
        status: str,
        prompt: str,
        response: Optional[str] = None,
        error_message: Optional[str] = None,
        model_id: Optional[int] = None,
        provider_id: Optional[int] = None,
        latency_ms: Optional[int] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
        cache_hit: bool = False,
        fallback_used: bool = False
    ) -> AIAuditLog:
        """Create a new audit log entry"""
        log = AIAuditLog(
            feature=feature,
            status=status,
            prompt=prompt,
            response=response,
            error_message=error_message,
            model_id=model_id,
            provider_id=provider_id,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            cache_hit=cache_hit,
            fallback_used=fallback_used
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def get_recent(self, db: Session, limit: int = 100) -> List[AIAuditLog]:
        """Get recent audit logs"""
        return db.query(AIAuditLog).order_by(
            AIAuditLog.created_at.desc()
        ).limit(limit).all()


ai_audit_log_repo = AIAuditLogRepository()
