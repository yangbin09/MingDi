#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NodeFlow Repository - Database operations for NodeFlow entity.
"""
from typing import List
from sqlalchemy.orm import Session

from models import NodeFlow
from .base import BaseRepository


class NodeFlowRepository(BaseRepository):
    """Repository for NodeFlow entity"""

    def __init__(self) -> None:
        super().__init__(NodeFlow)

    def get_active(self, db: Session) -> List[NodeFlow]:
        """Get all active node flows"""
        return db.query(NodeFlow).filter(NodeFlow.is_active == True)  # noqa: E712.all()


# Singleton instance
node_flow_repo = NodeFlowRepository()
