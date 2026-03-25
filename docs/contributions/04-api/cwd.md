# API 设计与实现贡献说明

姓名：陈伟栋
学号：2312190218
日期：2026-03-25

## 我完成的工作

### 1. API 设计
- 用户认证 API（已有实现）
- 分类管理 API（7 个端点）
- 账户管理 API（9 个端点）
- 查询接口设计（支持分页、过滤、排序）
- RESTful 规范设计

### 2. 文档编写
- OpenAPI 文档（`docs/api.yaml`）
- API 使用说明（`docs/api.md` 已有）
- 剩余实现计划文档（`docs/api-remaining-plan.md`）

### 3. 前端实现
- 无（未参与前端开发）

### 4. 后端实现
- API 路由定义（`backend/app/api/categories.py`, `backend/app/api/accounts.py`）
- Schema 数据验证（`backend/app/schemas/category.py`, `backend/app/schemas/account.py`）
- 业务逻辑处理（分类CRUD、账户CRUD、账户转账、余额调整）
- 错误处理（统一响应格式、参数校验、业务校验）
- 路由注册（`backend/app/api/__init__.py`）

### 5. 测试
- [ ] Postman/Apifox 测试集合
- [ ] 后端单元测试
- [ ] 测试用例数量：0 个

## PR 链接
- 暂无（本地开发，尚未提交 PR）

## 遇到的问题和解决

### 问题 1：分类树结构递归构建
**问题**：需要返回带有 `children` 字段的树形结构，便于前端展示层级分类。

**解决**：实现了 `build_tree` 递归函数，根据 `parent_id` 关系构建树形结构：
```python
def build_tree(categories: List[Category], parent_id: Optional[int] = None) -> List[dict]:
    tree = []
    for cat in categories:
        if cat.parent_id == parent_id:
            cat_dict = CategoryResponse.model_validate(cat).model_dump()
            children = build_tree(categories, cat.id)
            cat_dict["children"] = children
            tree.append(cat_dict)
    return tree
```

### 问题 2：账户默认状态互斥
**问题**：用户只能有一个默认账户，设置新默认账户时需要取消其他账户的默认状态。

**解决**：在创建和更新账户时，如果 `is_default=True`，先将用户其他账户的 `is_default` 设为 `False`：
```python
if account_data.is_default:
    db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.is_default == True
    ).update({"is_default": False})
```

### 问题 3：账户转账的余额联动
**问题**：账户间转账需要同时创建两条交易记录并更新双方余额，需要保证数据一致性。

**解决**：在同一个数据库事务中完成：
1. 创建转出交易记录（type=transfer）
2. 创建转入交易记录（type=transfer）
3. 更新转出账户余额（减）
4. 更新转入账户余额（加）
5. 统一提交事务

## 心得体会

### 1. RESTful API 设计原则
通过本次实践，深入理解了 RESTful API 的设计原则：
- 使用名词复数作为资源路径（如 `/categories`、`/accounts`）
- 使用 HTTP 方法表示操作语义（GET/POST/PUT/DELETE）
- 合理使用 HTTP 状态码和统一响应格式

### 2. Pydantic 数据验证
掌握了 Pydantic v2 的使用方法：
- `BaseModel` 继承实现数据模型
- `Field()` 进行字段约束（长度、范围、正则等）
- `field_validator` 和 `model_validator` 实现自定义验证逻辑
- `model_dump(exclude_unset=True)` 实现部分更新

### 3. FastAPI 依赖注入
理解了 FastAPI 的依赖注入机制：
- `Depends(get_db)` 获取数据库会话
- `Depends(get_current_active_user)` 获取当前用户
- 通过依赖注入实现认证和权限控制

### 4. 业务逻辑与数据一致性
学会了处理复杂的业务逻辑：
- 删除前检查关联数据（分类下有交易记录不可删除）
- 多表操作的原子性（转账操作使用事务）
- 状态互斥处理（默认账户唯一性）

### 5. API 文档规范
学会了编写 OpenAPI 3.0 规范文档，包括：
- Schema 组件定义
- API 端点描述
- 请求/响应模型定义
- 认证方式配置
