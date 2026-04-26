"""
提醒管理 API 接口测试
"""
import pytest


class TestCreateReminder:
    """创建提醒测试"""

    def test_create_daily_reminder(self, client, auth_headers):
        """创建每日记账提醒"""
        response = client.post("/api/reminders", headers=auth_headers, json={
            "type": "daily",
            "title": "每日记账提醒",
            "content": "别忘了记录今天的支出",
            "remind_time": "21:00:00",
            "is_enabled": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "创建成功"
        assert data["data"]["type"] == "daily"
        assert data["data"]["title"] == "每日记账提醒"
        assert data["data"]["is_enabled"] is True

    def test_create_budget_reminder(self, client, auth_headers):
        """创建预算预警提醒"""
        response = client.post("/api/reminders", headers=auth_headers, json={
            "type": "budget",
            "title": "餐饮预算预警",
            "content": "餐饮支出已超预算",
            "remind_day": 15,
            "is_enabled": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["type"] == "budget"

    def test_create_reminder_invalid_time(self, client, auth_headers):
        """无效时间格式返回400"""
        response = client.post("/api/reminders", headers=auth_headers, json={
            "type": "daily",
            "title": "测试提醒",
            "remind_time": "25:00:00",
            "is_enabled": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400

    def test_create_reminder_unauthorized(self, client):
        """未认证时返回401"""
        response = client.post("/api/reminders", json={
            "type": "daily",
            "title": "测试"
        })
        assert response.status_code == 401


class TestGetReminders:
    """获取提醒测试"""

    def test_get_reminders_list(self, client, auth_headers):
        """获取提醒列表"""
        # 先创建
        client.post("/api/reminders", headers=auth_headers, json={
            "type": "daily", "title": "提醒1", "remind_time": "09:00:00"
        })
        client.post("/api/reminders", headers=auth_headers, json={
            "type": "budget", "title": "提醒2", "remind_day": 1
        })

        response = client.get("/api/reminders", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["total"] >= 2

    def test_get_reminders_filter_by_type(self, client, auth_headers):
        """按类型过滤提醒"""
        response = client.get("/api/reminders?reminder_type=daily", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        for r in data["data"]["reminders"]:
            assert r["type"] == "daily"

    def test_get_reminders_statistics(self, client, auth_headers):
        """获取提醒统计"""
        response = client.get("/api/reminders/statistics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "total" in data["data"]
        assert "enabled" in data["data"]
        assert "disabled" in data["data"]

    def test_check_today_reminders(self, client, auth_headers):
        """检查今日提醒"""
        response = client.get("/api/reminders/check-today", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "reminders" in data["data"]
        assert "current_time" in data["data"]


class TestReminderCRUD:
    """提醒 CRUD 测试"""

    def test_get_reminder_detail(self, client, auth_headers):
        """获取提醒详情"""
        create_resp = client.post("/api/reminders", headers=auth_headers, json={
            "type": "recurring", "title": "周期提醒", "remind_day": 25
        })
        reminder_id = create_resp.json()["data"]["id"]

        response = client.get(f"/api/reminders/{reminder_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == reminder_id
        assert data["data"]["title"] == "周期提醒"

    def test_get_reminder_not_found(self, client, auth_headers):
        """获取不存在的提醒返回404"""
        response = client.get("/api/reminders/99999", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 404

    def test_update_reminder(self, client, auth_headers):
        """更新提醒"""
        create_resp = client.post("/api/reminders", headers=auth_headers, json={
            "type": "daily", "title": "原标题", "remind_time": "08:00:00"
        })
        reminder_id = create_resp.json()["data"]["id"]

        response = client.put(f"/api/reminders/{reminder_id}", headers=auth_headers, json={
            "title": "新标题",
            "content": "新内容"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["title"] == "新标题"
        assert data["data"]["content"] == "新内容"

    def test_toggle_reminder(self, client, auth_headers):
        """切换提醒状态"""
        create_resp = client.post("/api/reminders", headers=auth_headers, json={
            "type": "daily", "title": "开关测试", "remind_time": "10:00:00"
        })
        reminder_id = create_resp.json()["data"]["id"]
        original_enabled = create_resp.json()["data"]["is_enabled"]

        response = client.patch(f"/api/reminders/{reminder_id}/toggle", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["is_enabled"] != original_enabled

    def test_delete_reminder(self, client, auth_headers):
        """删除提醒"""
        create_resp = client.post("/api/reminders", headers=auth_headers, json={
            "type": "report", "title": "待删除", "remind_day": 1
        })
        reminder_id = create_resp.json()["data"]["id"]

        response = client.delete(f"/api/reminders/{reminder_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "删除成功"

        # 验证已删除
        get_resp = client.get(f"/api/reminders/{reminder_id}", headers=auth_headers)
        assert get_resp.json()["code"] == 404
