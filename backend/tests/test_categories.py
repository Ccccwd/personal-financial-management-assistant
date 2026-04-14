"""
分类管理接口测试
"""
import pytest


class TestCategoriesEmpty:
    """分类空列表测试"""

    def test_get_categories_empty(self, client, auth_headers):
        """未创建分类时返回空列表"""
        response = client.get("/api/categories", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "success"
        # 只返回系统分类，自定义分类为空
        assert "data" in data
        assert "categories" in data["data"]


class TestCreateCategory:
    """创建分类测试"""

    def test_create_expense_category(self, client, auth_headers):
        """创建支出分类"""
        response = client.post("/api/categories", headers=auth_headers, json={
            "name": "餐饮",
            "type": "expense",
            "icon": "food",
            "color": "#FF6B6B"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "创建成功"
        assert data["data"]["name"] == "餐饮"
        assert data["data"]["type"] == "expense"
        assert data["data"]["is_system"] is False

    def test_create_income_category(self, client, auth_headers):
        """创建收入分类"""
        response = client.post("/api/categories", headers=auth_headers, json={
            "name": "工资",
            "type": "income",
            "icon": "wallet",
            "color": "#4ECDC4"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "工资"
        assert data["data"]["type"] == "income"

    def test_create_category_duplicate(self, client, auth_headers):
        """重复名称返回400"""
        # 创建第一个分类
        client.post("/api/categories", headers=auth_headers, json={
            "name": "餐饮",
            "type": "expense"
        })

        # 尝试创建同名分类
        response = client.post("/api/categories", headers=auth_headers, json={
            "name": "餐饮",
            "type": "expense"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 400
        assert "已存在" in data["message"]

    def test_create_category_with_parent(self, client, auth_headers):
        """创建带父分类的子分类"""
        # 先创建父分类
        parent_response = client.post("/api/categories", headers=auth_headers, json={
            "name": "餐饮",
            "type": "expense"
        })
        parent_id = parent_response.json()["data"]["id"]

        # 创建子分类
        response = client.post("/api/categories", headers=auth_headers, json={
            "name": "早餐",
            "type": "expense",
            "parent_id": parent_id
        })
        assert response.status_code == 200

        data = response.json()
        assert data["data"]["parent_id"] == parent_id

    def test_create_category_invalid_parent(self, client, auth_headers):
        """使用不存在的父分类返回400"""
        response = client.post("/api/categories", headers=auth_headers, json={
            "name": "测试",
            "type": "expense",
            "parent_id": 99999
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 400
        assert "父分类不存在" in data["message"]

    def test_create_category_unauthorized(self, client):
        """未认证时创建分类返回401"""
        response = client.post("/api/categories", json={
            "name": "测试",
            "type": "expense"
        })
        assert response.status_code == 401


class TestGetCategories:
    """获取分类列表测试"""

    def test_get_categories_list(self, client, auth_headers, test_category):
        """获取分类列表"""
        response = client.get("/api/categories", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["categories"]) > 0

    def test_get_categories_filter_by_type(self, client, auth_headers, test_category):
        """按类型过滤分类"""
        response = client.get("/api/categories?type=expense", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        for cat in data["data"]["categories"]:
            assert cat["type"] == "expense"

    def test_get_categories_exclude_system(self, client, auth_headers):
        """排除系统分类"""
        response = client.get("/api/categories?include_system=false", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        for cat in data["data"]["categories"]:
            assert cat["is_system"] is False


class TestCategoryTree:
    """分类树结构测试"""

    def test_get_category_tree(self, client, auth_headers):
        """获取分类树结构"""
        # 创建父分类
        parent_response = client.post("/api/categories", headers=auth_headers, json={
            "name": "餐饮",
            "type": "expense"
        })
        parent_id = parent_response.json()["data"]["id"]

        # 创建子分类
        client.post("/api/categories", headers=auth_headers, json={
            "name": "早餐",
            "type": "expense",
            "parent_id": parent_id
        })

        # 获取树结构
        response = client.get("/api/categories/tree", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        # 检查树结构包含 children 字段
        for cat in data["data"]:
            assert "children" in cat

    def test_get_category_tree_filter_type(self, client, auth_headers, test_category):
        """按类型过滤分类树"""
        response = client.get("/api/categories/tree?type=expense", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        for cat in data["data"]:
            assert cat["type"] == "expense"


class TestCategoryStats:
    """分类统计测试"""

    def test_get_categories_stats(self, client, auth_headers, test_category):
        """获取带统计的分类列表"""
        response = client.get("/api/categories/stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert "categories" in data["data"]
        # 检查统计字段
        for cat in data["data"]["categories"]:
            assert "transaction_count" in cat
            assert "total_amount" in cat


class TestUpdateCategory:
    """更新分类测试"""

    def test_update_category(self, client, auth_headers, test_category):
        """更新分类"""
        category_id = test_category["id"]

        response = client.put(f"/api/categories/{category_id}", headers=auth_headers, json={
            "name": "餐饮（更新）",
            "color": "#00FF00"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "餐饮（更新）"
        assert data["data"]["color"] == "#00FF00"

    def test_update_category_not_found(self, client, auth_headers):
        """更新不存在的分类返回404"""
        response = client.put("/api/categories/99999", headers=auth_headers, json={
            "name": "测试"
        })
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 404


class TestDeleteCategory:
    """删除分类测试"""

    def test_delete_category(self, client, auth_headers, test_category):
        """删除分类"""
        category_id = test_category["id"]

        response = client.delete(f"/api/categories/{category_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "删除成功"

    def test_delete_category_with_children(self, client, auth_headers):
        """有子分类时不可删除"""
        # 创建父分类
        parent_response = client.post("/api/categories", headers=auth_headers, json={
            "name": "餐饮",
            "type": "expense"
        })
        parent_id = parent_response.json()["data"]["id"]

        # 创建子分类
        client.post("/api/categories", headers=auth_headers, json={
            "name": "早餐",
            "type": "expense",
            "parent_id": parent_id
        })

        # 尝试删除父分类
        response = client.delete(f"/api/categories/{parent_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 400
        assert "子分类" in data["message"]

    def test_delete_category_not_found(self, client, auth_headers):
        """删除不存在的分类返回404"""
        response = client.delete("/api/categories/99999", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 404


class TestCategoryDetail:
    """分类详情测试"""

    def test_get_category_detail(self, client, auth_headers, test_category):
        """获取分类详情"""
        category_id = test_category["id"]

        response = client.get(f"/api/categories/{category_id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == category_id

    def test_get_category_detail_not_found(self, client, auth_headers):
        """获取不存在的分类返回404"""
        response = client.get("/api/categories/99999", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["code"] == 404
