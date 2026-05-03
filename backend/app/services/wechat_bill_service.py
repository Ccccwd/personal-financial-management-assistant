"""
微信账单解析服务
"""
import csv
import io
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal, InvalidOperation
import chardet

from app.schemas.wechat_bill import (
    ImportPreview, ValidateResponse
)


class WeChatBillService:
    """微信账单解析服务"""

    def __init__(self):
        self.field_mapping = {
            "交易时间": "transaction_time",
            "交易类型": "transaction_type",
            "交易对方": "counterparty",
            "商品": "description",
            "商品说明": "description",
            "收/付款方式": "payment_method",
            "金额(元)": "amount",
            "金额": "amount",
            "交易单号": "transaction_id",
            "商户单号": "merchant_order_id",
            "备注": "remark",
        }

        # 微信支出类型关键词
        self.expense_keywords = [
            "支出", "消费", "支付", "红包", "充值", "提现", "转出",
            "申购", "信用卡还款", "群付款", "亲属卡消费", "亲属卡充值",
        ]
        # 微信收入类型关键词
        self.income_keywords = [
            "收入", "收款", "退款", "转入", "赎回", "理财收益",
            "群收款", "亲属卡还款",
        ]

    def parse_csv_content(self, csv_content: str) -> ImportPreview:
        """解析微信CSV账单内容"""
        # 检测编码并解码
        raw_bytes = csv_content.encode('latin1', errors='replace')
        encoding = self._detect_encoding(raw_bytes)
        content = raw_bytes.decode(encoding, errors='replace')

        # 处理BOM
        if content.startswith('﻿'):
            content = content[1:]

        # 解析CSV
        rows = list(csv.reader(io.StringIO(content)))

        # 查找表头行
        header_row_index = self._find_header_row(rows)
        if header_row_index == -1:
            raise ValueError("未找到有效的账单数据行，请确认文件格式")

        headers = rows[header_row_index]
        data_rows = [
            row for row in rows[header_row_index + 1:]
            if row and len(row) > 3 and not row[0].startswith('总')
        ]

        parsed_transactions = []
        error_details = []
        potential_duplicates = 0
        income_count = 0
        expense_count = 0
        dates = []

        for i, row in enumerate(data_rows):
            try:
                transaction = self._parse_transaction_row(headers, row)
                if transaction:
                    # 重复检测
                    if self._is_potential_duplicate(transaction, parsed_transactions):
                        potential_duplicates += 1
                        transaction['is_potential_duplicate'] = True
                    else:
                        transaction['is_potential_duplicate'] = False

                    parsed_transactions.append(transaction)
                    dates.append(transaction['transaction_time'])

                    if transaction['transaction_type'] == 'income':
                        income_count += 1
                    else:
                        expense_count += 1
            except Exception as e:
                error_details.append({
                    "row_number": header_row_index + i + 2,
                    "error_type": "解析错误",
                    "error_message": str(e),
                })

        date_range = None
        if dates:
            date_range = {
                "start_date": min(dates).strftime("%Y-%m-%d"),
                "end_date": max(dates).strftime("%Y-%m-%d"),
            }

        return ImportPreview(
            filename="wechat_bill.csv",
            total_records=len(parsed_transactions),
            preview_data=parsed_transactions[:10],
            detected_format="微信账单CSV",
            potential_duplicates=potential_duplicates,
            income_count=income_count,
            expense_count=expense_count,
            date_range=date_range,
        )

    def validate_csv_format(self, file_content: bytes, filename: str) -> ValidateResponse:
        """验证CSV文件格式"""
        if not filename.lower().endswith('.csv'):
            return ValidateResponse(is_valid=False, message="请上传CSV格式文件")

        if len(file_content) > 10 * 1024 * 1024:
            return ValidateResponse(is_valid=False, message="文件过大，请上传小于10MB的文件")

        try:
            encoding = self._detect_encoding(file_content)
            content = file_content.decode(encoding, errors='replace')
            if content.startswith('﻿'):
                content = content[1:]

            rows = list(csv.reader(io.StringIO(content)))
            header_row_index = self._find_header_row(rows)
            if header_row_index == -1:
                return ValidateResponse(is_valid=False, message="未找到有效的微信账单表头")

            headers = rows[header_row_index]
            header_text = ' '.join(headers)
            for field in ["交易时间", "交易类型", "金额"]:
                if field not in header_text:
                    return ValidateResponse(is_valid=False, message=f"缺少必要字段: {field}")

            data_rows = [
                row for row in rows[header_row_index + 1:]
                if row and len(row) > 3 and not row[0].startswith('总')
            ]
            if not data_rows:
                return ValidateResponse(is_valid=False, message="未找到有效的交易数据")

            return ValidateResponse(
                is_valid=True,
                message="文件格式验证通过",
                file_info={
                    "total_records": len(data_rows),
                    "encoding": encoding,
                    "file_size": len(file_content),
                }
            )
        except Exception as e:
            return ValidateResponse(is_valid=False, message=f"文件验证失败: {str(e)}")

    def import_transactions(self, db, user_id: int, transactions: List[dict],
                           account_id: Optional[int] = None,
                           category_id: Optional[int] = None) -> dict:
        """批量导入交易记录到数据库"""
        from app.models.transaction import Transaction
        from app.models.account import Account
        from app.models.import_log import ImportLog, ImportStatus

        # 创建导入日志
        import_log = ImportLog(
            user_id=user_id,
            source="wechat",
            status=ImportStatus.PROCESSING,
            total_records=len(transactions),
        )
        db.add(import_log)
        db.commit()
        db.refresh(import_log)

        success_count = 0
        failed_count = 0
        skipped_count = 0
        errors = []

        # 获取默认账户
        if not account_id:
            account = db.query(Account).filter(
                Account.user_id == user_id,
                Account.is_default
            ).first()
            if not account:
                account = db.query(Account).filter(
                    Account.user_id == user_id
                ).first()
            if account:
                account_id = account.id

        for i, txn_data in enumerate(transactions):
            try:
                # 跳过重复
                if txn_data.get('is_potential_duplicate'):
                    skipped_count += 1
                    continue

                # 检查数据库中是否已存在（按微信交易单号）
                wechat_txn_id = txn_data.get('transaction_id', '')
                if wechat_txn_id:
                    existing = db.query(Transaction).filter(
                        Transaction.user_id == user_id,
                        Transaction.wechat_transaction_id == wechat_txn_id
                    ).first()
                    if existing:
                        skipped_count += 1
                        continue

                # 创建交易记录
                txn_type = "expense" if txn_data.get('transaction_type') == 'expense' else "income"
                amount = Decimal(str(txn_data.get('amount', 0)))
                if amount < 0:
                    amount = abs(amount)
                    txn_type = "expense"

                transaction = Transaction(
                    user_id=user_id,
                    type=txn_type,
                    amount=amount,
                    account_id=account_id,
                    category_id=category_id,
                    transaction_date=txn_data['transaction_time'],
                    remark=txn_data.get('description', '') or txn_data.get('remark', ''),
                    merchant_name=txn_data.get('counterparty', ''),
                    source="wechat",
                    wechat_transaction_id=wechat_txn_id or None,
                )
                db.add(transaction)
                success_count += 1

            except Exception as e:
                failed_count += 1
                errors.append({
                    "row": i + 1,
                    "error": str(e),
                    "data": txn_data,
                })

        db.commit()

        # 更新导入日志
        import_log.success_records = success_count
        import_log.failed_records = failed_count
        import_log.skipped_records = skipped_count
        import_log.error_details = errors if errors else None
        import_log.status = ImportStatus.COMPLETED if failed_count == 0 else ImportStatus.PARTIAL
        import_log.import_summary = f"成功{success_count}条，跳过{skipped_count}条，失败{failed_count}条"
        db.commit()

        return {
            "import_log_id": import_log.id,
            "success_count": success_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "total": len(transactions),
        }

    def _detect_encoding(self, content: bytes) -> str:
        """检测文件编码"""
        try:
            result = chardet.detect(content)
            encoding = result.get('encoding', 'utf-8') or 'utf-8'
            encoding_map = {'GB2312': 'gbk', 'GBK': 'gbk', 'UTF-8-SIG': 'utf-8', 'ascii': 'utf-8'}
            return encoding_map.get(encoding, encoding)
        except Exception:
            return 'utf-8'

    def _find_header_row(self, rows: List[List[str]]) -> int:
        """查找表头行"""
        for i, row in enumerate(rows):
            if len(row) >= 5:
                row_text = ' '.join(row)
                if any(kw in row_text for kw in ["交易时间", "交易类型", "金额"]):
                    return i
        return -1

    def _parse_transaction_row(self, headers: List[str], row: List[str]) -> Optional[Dict[str, Any]]:
        """解析单行交易数据"""
        if len(row) < len(headers):
            return None

        transaction = {}
        for i, header in enumerate(headers):
            if i < len(row) and header.strip():
                key = self.field_mapping.get(header.strip(), header.strip())
                transaction[key] = row[i].strip()

        # 解析交易时间
        transaction_time = self._parse_time(transaction.get('transaction_time', ''))
        if not transaction_time:
            raise ValueError("交易时间格式错误")

        # 解析类型
        txn_type_str = transaction.get('transaction_type', '')
        txn_type = self._map_type(txn_type_str)

        # 解析金额
        amount = self._parse_amount(transaction.get('amount', ''))
        if amount is None:
            raise ValueError("金额格式错误")

        return {
            'transaction_time': transaction_time,
            'transaction_type': txn_type,
            'counterparty': transaction.get('counterparty', ''),
            'description': transaction.get('description', ''),
            'payment_method': transaction.get('payment_method', ''),
            'amount': float(amount),
            'transaction_id': transaction.get('transaction_id', ''),
            'merchant_order_id': transaction.get('merchant_order_id', ''),
            'remark': transaction.get('remark', ''),
        }

    def _parse_time(self, time_str: str) -> Optional[datetime]:
        """解析交易时间"""
        if not time_str:
            return None
        formats = [
            "%Y年%m月%d日 %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y%m%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        return None

    def _map_type(self, wechat_type: str) -> str:
        """映射微信交易类型"""
        for kw in self.expense_keywords:
            if kw in wechat_type:
                return "expense"
        for kw in self.income_keywords:
            if kw in wechat_type:
                return "income"
        return "expense"

    def _parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """解析金额"""
        if not amount_str:
            return None
        clean = re.sub(r'[￥¥,\s]', '', amount_str.strip())
        is_negative = False
        if clean.startswith('-'):
            is_negative = True
            clean = clean[1:]
        elif clean.startswith('+'):
            clean = clean[1:]
        try:
            amount = Decimal(clean)
            return -amount if is_negative else amount
        except InvalidOperation:
            return None

    def _is_potential_duplicate(self, new_txn: Dict, existing: List[Dict]) -> bool:
        """检查潜在重复交易"""
        for ex in existing:
            if (abs((new_txn['transaction_time'] - ex['transaction_time']).total_seconds()) < 60
                    and new_txn['amount'] == ex['amount']
                    and new_txn.get('description') == ex.get('description')):
                return True
        return False
