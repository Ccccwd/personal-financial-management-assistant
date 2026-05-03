"""
AI 智能服务模块
提供账单智能分类和理财建议生成功能
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from openai import OpenAI

from app.config.settings import settings
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.ai_advice_record import AIAdviceRecord


class AIService:
    """AI 智能服务类"""

    # 规则分类器 - 优先使用，节省 Token
    RULES = {
        "餐饮": [
            "餐厅", "外卖", "咖啡", "奶茶", "火锅", "烧烤",
            "麦当劳", "肯德基", "瑞幸", "星巴克", "美团", "饿了么",
            "喜茶", "奈雪", "茶百道", "古茗", "蜜雪冰城"
        ],
        "交通": [
            "滴滴", "出租", "地铁", "公交", "加油", "停车",
            "高铁", "机票", "火车", "客车", "哈啰", "摩拜",
            "共享单车", "优步", "神州租车"
        ],
        "购物": [
            "淘宝", "京东", "拼多多", "超市", "便利店", "商场",
            "天猫", "苏宁", "国美", "唯品会", "当当", "亚马逊"
        ],
        "娱乐": [
            "电影", "游戏", "KTV", "酒吧", "旅游", "网吧",
            "影院", "乐园", "健身", "音乐会", "展览"
        ],
        "医疗": [
            "医院", "药店", "诊所", "体检", "药房", "挂号",
            "疫苗", "体检中心"
        ],
        "教育": [
            "培训", "课程", "书籍", "学费", "教育", "学习",
            "辅导", "考试", "学校"
        ],
        "住房": [
            "房租", "物业", "水电", "燃气", "采暖", "宽带",
            "装修", "家居", "房产"
        ],
        "通讯": [
            "话费", "流量", "宽带", "充值", "通讯", "移动",
            "联通", "电信"
        ],
        "金融": [
            "理财", "基金", "股票", "保险", "银行", "借贷",
            "还款", "贷款", "证券"
        ],
    }

    # 默认分类（当无法匹配时使用）
    DEFAULT_CATEGORY = "其他"

    def __init__(self):
        """初始化 AI 服务"""
        self._client = None

    @property
    def client(self) -> OpenAI:
        """懒加载 OpenAI 客户端"""
        if self._client is None:
            self._client = OpenAI(
                api_key=settings.ai_api_key,
                base_url=settings.ai_base_url
            )
        return self._client

    def _match_by_rules(self, merchant_name: str, transaction_type: str) -> Optional[str]:
        """
        使用规则匹配分类

        Args:
            merchant_name: 商户名称
            transaction_type: 交易类型

        Returns:
            匹配到的分类名称，未匹配返回 None
        """
        if not merchant_name:
            return None

        merchant_lower = merchant_name.lower()

        for category_name, keywords in self.RULES.items():
            for keyword in keywords:
                if keyword.lower() in merchant_lower:
                    return category_name

        return None

    def _find_category_by_name(
        self,
        db: Session,
        user_id: int,
        category_name: str,
        transaction_type: str
    ) -> Optional[Category]:
        """
        根据分类名称查找用户分类

        Args:
            db: 数据库会话
            user_id: 用户ID
            category_name: 分类名称
            transaction_type: 交易类型

        Returns:
            匹配的分类对象，未找到返回 None
        """
        return db.query(Category).filter(
            Category.user_id == user_id,
            Category.name == category_name,
            Category.type == transaction_type
        ).first()

    def classify_by_llm(
        self,
        db: Session,
        user_id: int,
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        使用 LLM 进行批量分类

        Args:
            db: 数据库会话
            user_id: 用户ID
            items: 待分类的交易列表

        Returns:
            分类结果列表
        """
        # 获取用户的分类列表
        categories = db.query(Category).filter(
            (Category.user_id == user_id) | (Category.is_system),
            Category.type == "expense"
        ).all()

        category_list = [
            {"id": c.id, "name": c.name, "is_system": c.is_system}
            for c in categories
        ]

        # 构建分类 prompt
        items_text = "\n".join([
            f"{i + 1}. 商户: {item['merchant_name']}, "
            f"商品: {item.get('product_name', '无')}, "
            f"微信分类: {item.get('wechat_category', '无')}, "
            f"金额: {item['amount']}, "
            f"类型: {item['transaction_type']}"
            for i, item in enumerate(items)
        ])

        category_text = "\n".join([
            f"- {c['name']} (ID: {c['id']})"
            for c in category_list
        ])

        prompt = f"""你是一个专业的账单分类助手。请根据以下信息，将每笔交易归类到最合适的分类中。

可用分类列表：
{category_text}

待分类的交易：
{items_text}

请以 JSON 格式返回结果，格式如下：
[
  {{
    "index": 0,
    "category_id": 123,
    "category_name": "餐饮",
    "confidence": 0.95
  }}
]

注意：
1. index 对应待分类交易的索引（从 0 开始）
2. category_id 必须从可用分类列表中选择
3. confidence 表示分类置信度（0-1 之间的浮点数）
4. 确保返回的是有效的 JSON 格式
5. 如果无法确定分类，请选择"其他"或最接近的分类
"""

        try:
            response = self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            if isinstance(result, dict) and "results" in result:
                result = result["results"]

            return result

        except Exception as e:
            # LLM 调用失败，返回默认分类
            print(f"LLM 分类失败: {str(e)}")
            # 找到"其他"分类
            other_category = db.query(Category).filter(
                (Category.user_id == user_id) | (Category.is_system),
                Category.name == "其他",
                Category.type == "expense"
            ).first()

            category_id = other_category.id if other_category else None

            return [
                {
                    "index": i,
                    "category_id": category_id,
                    "category_name": "其他",
                    "confidence": 0.5
                }
                for i in range(len(items))
            ]

    def classify_items(
        self,
        db: Session,
        user_id: int,
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量分类交易记录

        先使用规则匹配，匹配不上的再调用 LLM

        Args:
            db: 数据库会话
            user_id: 用户ID
            items: 待分类的交易列表

        Returns:
            分类结果字典
        """
        results = []
        rule_matched_indices = []
        llm_items = []

        # 第一轮：规则匹配
        for i, item in enumerate(items):
            merchant_name = item.get("merchant_name", "")
            transaction_type = item.get("transaction_type", "expense")

            matched_category = self._match_by_rules(merchant_name, transaction_type)

            if matched_category:
                category = self._find_category_by_name(
                    db, user_id, matched_category, transaction_type
                )

                results.append({
                    "index": i,
                    "merchant_name": merchant_name,
                    "category_id": category.id if category else None,
                    "category_name": matched_category,
                    "confidence": 0.9,
                    "matched_by": "rule"
                })
                rule_matched_indices.append(i)
            else:
                llm_items.append((i, item))

        # 第二轮：LLM 分类
        llm_called_count = 0

        if llm_items:
            llm_called_count = 1
            llm_indices = [idx for idx, _ in llm_items]
            llm_items_data = [item for _, item in llm_items]

            llm_response = self.classify_by_llm(db, user_id, llm_items_data)

            # 构建 LLM 结果映射
            llm_result_map = {}
            for r in llm_response:
                llm_result_map[r.get("index", 0)] = r

            # 将 LLM 结果插入正确位置
            for i, original_idx in enumerate(llm_indices):
                llm_result = llm_result_map.get(i, {})
                item = llm_items[i][1]

                results.append({
                    "index": original_idx,
                    "merchant_name": item.get("merchant_name", ""),
                    "category_id": llm_result.get("category_id"),
                    "category_name": llm_result.get("category_name", "未知"),
                    "confidence": llm_result.get("confidence", 0.7),
                    "matched_by": "llm"
                })

        # 排序结果
        results.sort(key=lambda x: x["index"])

        return {
            "results": results,
            "total": len(results),
            "llm_called_count": llm_called_count,
            "rule_matched_count": len(rule_matched_indices)
        }

    def reclassify_transaction(
        self,
        db: Session,
        user_id: int,
        transaction_id: int
    ) -> Dict[str, Any]:
        """
        重新分类单条交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            transaction_id: 交易ID

        Returns:
            分类结果
        """
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()

        if not transaction:
            return None

        item = {
            "merchant_name": transaction.merchant_name or "",
            "product_name": transaction.product_name,
            "amount": float(transaction.amount),
            "transaction_type": transaction.type
        }

        # 先尝试规则匹配
        matched = self._match_by_rules(item["merchant_name"], item["transaction_type"])

        if matched:
            category = self._find_category_by_name(
                db, user_id, matched, item["transaction_type"]
            )
            return {
                "transaction_id": transaction_id,
                "category_id": category.id if category else None,
                "category_name": matched,
                "confidence": 0.9,
                "matched_by": "rule"
            }

        # 规则不匹配，调用 LLM
        result = self.classify_by_llm(db, user_id, [item])

        if result and len(result) > 0:
            return {
                "transaction_id": transaction_id,
                "category_id": result[0].get("category_id"),
                "category_name": result[0].get("category_name", "未知"),
                "confidence": result[0].get("confidence", 0.7),
                "matched_by": "llm"
            }

        return None

    def generate_advice(
        self,
        db: Session,
        user: User,
        months: int = 3
    ) -> Dict[str, Any]:
        """
        生成理财建议

        Args:
            db: 数据库会话
            user: 用户对象
            months: 分析最近几个月的数据

        Returns:
            理财建议字典
        """
        # 计算分析周期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)

        # 检查是否有缓存
        cached = db.query(AIAdviceRecord).filter(
            AIAdviceRecord.user_id == user.id,
            AIAdviceRecord.analysis_period_start >= start_date,
            AIAdviceRecord.analysis_period_end <= end_date,
            not AIAdviceRecord.from_cache
        ).order_by(AIAdviceRecord.created_at.desc()).first()

        if cached:
            return {
                "generated_at": cached.created_at,
                "from_cache": True,
                "analysis_period": {
                    "start": cached.analysis_period_start,
                    "end": cached.analysis_period_end
                },
                "advice": {
                    "highlights": cached.highlights,
                    "warnings": cached.warnings,
                    "suggestions": cached.suggestions,
                    "next_month_budget": cached.budget_suggestion,
                    "full_report": cached.full_report
                }
            }

        # 查询交易数据
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).all()

        if not transactions:
            return {
                "generated_at": datetime.now(),
                "from_cache": False,
                "analysis_period": {"start": start_date, "end": end_date},
                "advice": {
                    "highlights": ["暂无交易数据"],
                    "warnings": [],
                    "suggestions": ["建议开始记录您的收支情况"],
                    "next_month_budget": None,
                    "full_report": "您暂无交易数据，建议开始记录您的收支情况以获得更好的理财建议。"
                }
            }

        # 按分类汇总支出
        category_stats = {}
        total_expense = 0

        for t in transactions:
            if t.type == "expense":
                category_name = t.category.name if t.category else "未分类"
                amount = float(t.amount)
                category_stats[category_name] = category_stats.get(category_name, 0) + amount
                total_expense += amount

        # 构建分析数据
        summary_data = {
            "period": f"{months}个月",
            "total_expense": round(total_expense, 2),
            "transaction_count": len(transactions),
            "category_breakdown": [
                {"category": k, "amount": round(v, 2), "percentage": round(v / total_expense * 100, 1) if total_expense > 0 else 0}
                for k, v in sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
            ]
        }

        # 构建提示词
        prompt = f"""你是一位专业的理财顾问。请分析以下用户的消费数据，提供个性化的理财建议。

用户基本信息：
- 分析周期：最近 {months} 个月
- 总支出：{summary_data['total_expense']} 元
- 交易笔数：{summary_data['transaction_count']} 笔

分类支出明细：
{json.dumps(summary_data['category_breakdown'], ensure_ascii=False, indent=2)}

请以 JSON 格式返回分析结果，包含以下字段：
{{
  "highlights": ["消费亮点1", "消费亮点2"],
  "warnings": ["预警信息1", "预警信息2"],
  "suggestions": ["建议1", "建议2", "建议3"],
  "next_month_budget": {{
    "总预算": 金额,
    "各分类预算": {{"分类名": 金额}}
  }},
  "full_report": "完整的理财建议报告文本"
}}

注意：
1. highlights 应该肯定用户的良好消费习惯
2. warnings 应该指出可能的消费问题
3. suggestions 应该提供具体的改进建议
4. next_month_budget 根据历史数据给出合理的下月预算建议
5. full_report 是一段完整的、友好的理财建议文本
6. 确保返回的是有效的 JSON 格式
"""

        try:
            response = self.client.chat.completions.create(
                model=settings.ai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            advice_data = json.loads(content)

            # 计算消耗的 Token
            tokens_used = response.usage.total_tokens if hasattr(response, "usage") else 0

            # 保存到数据库
            record = AIAdviceRecord(
                user_id=user.id,
                advice_type="financial",
                analysis_period_start=start_date,
                analysis_period_end=end_date,
                highlights=advice_data.get("highlights", []),
                warnings=advice_data.get("warnings", []),
                suggestions=advice_data.get("suggestions", []),
                budget_suggestion=advice_data.get("next_month_budget"),
                full_report=advice_data.get("full_report", ""),
                tokens_used=tokens_used,
                from_cache=False
            )
            db.add(record)
            db.commit()

            return {
                "generated_at": record.created_at,
                "from_cache": False,
                "analysis_period": {"start": start_date, "end": end_date},
                "advice": {
                    "highlights": record.highlights,
                    "warnings": record.warnings,
                    "suggestions": record.suggestions,
                    "next_month_budget": record.budget_suggestion,
                    "full_report": record.full_report
                }
            }

        except Exception as e:
            print(f"生成建议失败: {str(e)}")
            return {
                "generated_at": datetime.now(),
                "from_cache": False,
                "analysis_period": {"start": start_date, "end": end_date},
                "advice": {
                    "highlights": [],
                    "warnings": [],
                    "suggestions": ["AI 服务暂时不可用，请稍后再试"],
                    "next_month_budget": None,
                    "full_report": "抱歉，AI 服务暂时不可用，请稍后再试。"
                }
            }

    def get_usage_stats(
        self,
        db: Session,
        user_id: int,
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """
        获取用量统计

        Args:
            db: 数据库会话
            user_id: 用户ID
            year: 年份
            month: 月份

        Returns:
            用量统计字典
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)

        records = db.query(AIAdviceRecord).filter(
            AIAdviceRecord.user_id == user_id,
            AIAdviceRecord.created_at >= start_date,
            AIAdviceRecord.created_at <= end_date
        ).all()

        total_tokens = sum(r.tokens_used for r in records)

        return {
            "month": f"{year}-{month:02d}",
            "classify_calls": 0,  # 分类调用暂不记录
            "advice_calls": len(records),
            "total_tokens_used": total_tokens
        }
