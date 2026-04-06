#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NodeFlow Service - Business logic for NodeFlow (Visual DAG) operations.
"""
from typing import List, Optional, Dict, Any
import json
from collections import deque
from sqlalchemy.orm import Session

from models import NodeFlow
from schemas import NodeFlowCreate, NodeFlowUpdate
from repositories import node_flow_repo, task_repo
from scheduler import execute_task_now


class NodeFlowService:
    """Service layer for NodeFlow business logic"""

    def list_node_flows(self, db: Session) -> List[NodeFlow]:
        """Get all node flows"""
        return node_flow_repo.get_all(db)

    def get_node_flow(self, db: Session, flow_id: int) -> Optional[NodeFlow]:
        """Get node flow by ID"""
        return node_flow_repo.get_by_id(db, flow_id)

    def create_node_flow(self, db: Session, flow_data: NodeFlowCreate) -> NodeFlow:
        """Create a new node flow"""
        flow = NodeFlow(
            name=flow_data.name,
            description=flow_data.description,
            nodes=flow_data.nodes,
            edges=flow_data.edges,
            is_active=flow_data.is_active
        )
        db.add(flow)
        db.commit()
        db.refresh(flow)
        return flow

    def update_node_flow(
        self,
        db: Session,
        flow_id: int,
        flow_data: NodeFlowUpdate
    ) -> Optional[NodeFlow]:
        """Update a node flow"""
        flow = node_flow_repo.get_by_id(db, flow_id)
        if not flow:
            return None

        update_dict = flow_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None and hasattr(flow, key):
                setattr(flow, key, value)

        db.commit()
        db.refresh(flow)
        return flow

    def delete_node_flow(self, db: Session, flow_id: int) -> bool:
        """Delete a node flow"""
        return node_flow_repo.delete(db, flow_id)

    def execute_node_flow(
        self,
        db: Session,
        flow_id: int
    ) -> Dict[str, Any]:
        """
        Execute a node flow (DAG) in topological order.
        Returns execution result with order and task statuses.
        """
        flow = node_flow_repo.get_by_id(db, flow_id)
        if not flow:
            raise ValueError("Node flow not found")

        try:
            nodes = json.loads(flow.nodes) if isinstance(flow.nodes, str) else flow.nodes
            edges = json.loads(flow.edges) if isinstance(flow.edges, str) else flow.edges
        except json.JSONDecodeError:
            raise ValueError("Invalid node/edge data")

        # Build adjacency list and in-degree map for topological sort
        in_degree = {node['id']: 0 for node in nodes}
        adjacency = {node['id']: [] for node in nodes}

        for edge in edges:
            adjacency[edge['source']].append(edge['target'])
            in_degree[edge['target']] += 1

        # Kahn's algorithm with deque for O(1) popleft
        queue = deque([
            node['id'] for node in nodes
            if in_degree[node['id']] == 0
        ])
        execution_order: List[int] = []

        while queue:
            node_id = queue.popleft()
            execution_order.append(node_id)

            for neighbor in adjacency[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Bulk fetch tasks to avoid N+1 queries
        task_ids = [
            n['task_id'] for n in nodes
            if isinstance(n, dict) and n.get('task_id')
        ]
        task_map = task_repo.get_by_ids(db, task_ids) if task_ids else {}
        node_map = {n['id']: n for n in nodes}

        # Execute tasks in topological order
        results: List[Dict[str, Any]] = []
        for node_id in execution_order:
            node = node_map.get(node_id)
            if node and node.get('task_id'):
                task = task_map.get(node['task_id'])
                if task:
                    execute_task_now(task.id)
                    results.append({
                        "node_id": node_id,
                        "task_id": task.id,
                        "task_name": task.name,
                        "status": "triggered"
                    })

        return {
            "success": True,
            "flow_id": flow_id,
            "execution_order": execution_order,
            "results": results
        }


# Singleton instance
node_flow_service = NodeFlowService()
