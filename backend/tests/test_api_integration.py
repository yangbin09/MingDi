#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for API endpoints.
Tests full request/response cycle with test database.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient


class TestTaskAPI:
    """Integration tests for Task API endpoints"""

    def test_list_tasks_empty(self, client: TestClient) -> None:
        """Test GET /api/tasks returns empty list"""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_tasks_with_data(self, client: TestClient, sample_task) -> None:
        """Test GET /api/tasks returns tasks"""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Task"

    def test_get_task_found(self, client: TestClient, sample_task) -> None:
        """Test GET /api/tasks/{id} returns task"""
        response = client.get(f"/api/tasks/{sample_task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Task"

    def test_get_task_not_found(self, client: TestClient) -> None:
        """Test GET /api/tasks/{id} returns 404"""
        response = client.get("/api/tasks/9999")
        assert response.status_code == 404

    def test_create_task(self, client: TestClient) -> None:
        """Test POST /api/tasks creates task"""
        payload = {
            "name": "New Task",
            "script_path": "./new.py",
            "is_active": True,
        }
        response = client.post("/api/tasks", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Task"
        assert data["id"] is not None

    def test_create_task_with_webhook(self, client: TestClient) -> None:
        """Test POST /api/tasks with webhook enabled"""
        payload = {
            "name": "Webhook Task",
            "script_path": "./webhook.py",
            "webhook_enabled": True,
        }
        response = client.post("/api/tasks", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["webhook_enabled"] is True
        assert data["webhook_token"] is not None

    def test_update_task(self, client: TestClient, sample_task) -> None:
        """Test PUT /api/tasks/{id} updates task"""
        payload = {"name": "Updated Name"}
        response = client.put(f"/api/tasks/{sample_task.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_delete_task(self, client: TestClient, sample_task) -> None:
        """Test DELETE /api/tasks/{id} deletes task"""
        response = client.delete(f"/api/tasks/{sample_task.id}")
        assert response.status_code == 200

        # Verify deleted
        response = client.get(f"/api/tasks/{sample_task.id}")
        assert response.status_code == 404

    def test_run_task(self, client: TestClient, sample_task) -> None:
        """Test POST /api/tasks/{id}/run triggers execution"""
        response = client.post(f"/api/tasks/{sample_task.id}/run")
        assert response.status_code == 200
        assert "execution started" in response.json()["message"]


class TestLogAPI:
    """Integration tests for Log API endpoints"""

    def test_get_task_logs_empty(self, client: TestClient, sample_task) -> None:
        """Test GET /api/tasks/{id}/logs returns empty"""
        response = client.get(f"/api/tasks/{sample_task.id}/logs")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_task_logs_with_data(self, client: TestClient, sample_task, sample_log) -> None:
        """Test GET /api/tasks/{id}/logs returns logs"""
        response = client.get(f"/api/tasks/{sample_task.id}/logs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["output"] == "Test output"

    def test_get_log_found(self, client: TestClient, sample_log) -> None:
        """Test GET /api/logs/{id} returns log"""
        response = client.get(f"/api/logs/{sample_log.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["output"] == "Test output"

    def test_get_log_not_found(self, client: TestClient) -> None:
        """Test GET /api/logs/{id} returns 404"""
        response = client.get("/api/logs/9999")
        assert response.status_code == 404

    def test_search_logs(self, client: TestClient, sample_task, sample_log) -> None:
        """Test GET /api/logs/search with filters"""
        response = client.get("/api/logs/search")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    def test_search_logs_with_keyword(self, client: TestClient, sample_task, sample_log) -> None:
        """Test GET /api/logs/search with keyword filter"""
        response = client.get("/api/logs/search?keyword=Test")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_search_logs_pagination(self, client: TestClient, sample_task, sample_log) -> None:
        """Test GET /api/logs/search with pagination"""
        response = client.get("/api/logs/search?page=1&size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1

    def test_delete_log(self, client: TestClient, sample_log) -> None:
        """Test DELETE /api/logs/{id} deletes log"""
        response = client.delete(f"/api/logs/{sample_log.id}")
        assert response.status_code == 200

    def test_batch_delete_logs(self, client: TestClient, db: Session, sample_task) -> None:
        """Test DELETE /api/logs with batch IDs"""
        # Create logs using the db fixture directly
        logs = []
        for i in range(3):
            from models import Log
            log = Log(
                task_id=sample_task.id,
                start_time=datetime.now(),
                output=f"Log {i}",
                exit_code=0,
            )
            db.add(log)
            logs.append(log)
        db.commit()

        # Get IDs
        ids = [log_obj.id for log_obj in logs]

        response = client.delete("/api/logs", json=ids)
        assert response.status_code == 200


class TestTimelineAPI:
    """Integration tests for Timeline endpoint"""

    def test_get_timeline_empty(self, client: TestClient) -> None:
        """Test GET /api/tasks/timeline returns empty when no logs"""
        response = client.get("/api/tasks/timeline")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_timeline_with_logs(self, client: TestClient, sample_task, sample_log) -> None:
        """Test GET /api/tasks/timeline returns timeline data"""
        response = client.get("/api/tasks/timeline")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["task_name"] == "Test Task"
        assert data[0]["exit_code"] == 0


class TestEnvVarAPI:
    """Integration tests for EnvVar API endpoints"""

    def test_list_env_vars_empty(self, client: TestClient) -> None:
        """Test GET /api/env-vars returns empty"""
        response = client.get("/api/env-vars")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_env_var(self, client: TestClient) -> None:
        """Test POST /api/env-vars creates variable"""
        payload = {"key": "TEST_KEY", "value": "test_value"}
        response = client.post("/api/env-vars", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "TEST_KEY"

    def test_create_env_var_duplicate(self, client: TestClient, sample_env_var) -> None:
        """Test POST /api/env-vars with duplicate key returns 400"""
        payload = {"key": "TEST_VAR", "value": "new_value"}
        response = client.post("/api/env-vars", json=payload)
        assert response.status_code == 400

    def test_export_env_vars(self, client: TestClient, sample_env_var) -> None:
        """Test GET /api/env-vars/export returns dict"""
        response = client.get("/api/env-vars/export")
        assert response.status_code == 200
        data = response.json()
        assert "TEST_VAR" in data
        assert data["TEST_VAR"] == "test_value"


class TestAlertAPI:
    """Integration tests for Alert API endpoints"""

    def test_list_alerts_empty(self, client: TestClient) -> None:
        """Test GET /api/alerts returns empty"""
        response = client.get("/api/alerts")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_alert(self, client: TestClient) -> None:
        """Test POST /api/alerts creates alert"""
        payload = {
            "name": "Test Alert",
            "webhook_url": "http://test.com/hook",
            "events": "failed,timeout",
        }
        response = client.post("/api/alerts", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Alert"

    def test_update_alert(self, client: TestClient, sample_alert) -> None:
        """Test PUT /api/alerts/{id} updates alert"""
        payload = {"name": "Updated Alert"}
        response = client.put(f"/api/alerts/{sample_alert.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Alert"

    def test_delete_alert(self, client: TestClient, sample_alert) -> None:
        """Test DELETE /api/alerts/{id} deletes alert"""
        response = client.delete(f"/api/alerts/{sample_alert.id}")
        assert response.status_code == 200


class TestWebhookAPI:
    """Integration tests for Webhook endpoints"""

    def test_enable_webhook(self, client: TestClient, sample_task) -> None:
        """Test POST /api/tasks/{id}/enable-webhook enables webhook"""
        response = client.post(f"/api/tasks/{sample_task.id}/enable-webhook")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "webhook_url" in data

    def test_disable_webhook(self, client: TestClient, sample_task) -> None:
        """Test POST /api/tasks/{id}/disable-webhook disables webhook"""
        # First enable
        client.post(f"/api/tasks/{sample_task.id}/enable-webhook")
        # Then disable
        response = client.post(f"/api/tasks/{sample_task.id}/disable-webhook")
        assert response.status_code == 200

    def test_get_webhook_info(self, client: TestClient, sample_task) -> None:
        """Test GET /api/tasks/{id}/webhook-info returns info"""
        response = client.get(f"/api/tasks/{sample_task.id}/webhook-info")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == sample_task.id

    def test_trigger_webhook_invalid_token(self, client: TestClient) -> None:
        """Test GET /api/webhook/{token} with invalid token returns 404"""
        response = client.get("/api/webhook/invalid_token")
        assert response.status_code == 404


class TestHealthAPI:
    """Integration tests for Health and System endpoints"""

    def test_health_check(self, client: TestClient) -> None:
        """Test GET /api/health returns ok"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_root(self, client: TestClient) -> None:
        """Test GET /api/ returns message"""
        response = client.get("/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
