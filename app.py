#!/usr/bin/env python3
"""简单记账程序（命令行版）。"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import List


DEFAULT_DB = Path("ledger.json")


@dataclass
class Record:
    id: int
    type: str
    amount: float
    category: str
    note: str
    date: str


class Ledger:
    def __init__(self, db_path: Path = DEFAULT_DB):
        self.db_path = db_path
        self.records: List[Record] = []
        self._load()

    def _load(self) -> None:
        if not self.db_path.exists():
            self.records = []
            return
        data = json.loads(self.db_path.read_text(encoding="utf-8"))
        self.records = [Record(**item) for item in data]

    def _save(self) -> None:
        data = [asdict(item) for item in self.records]
        self.db_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _next_id(self) -> int:
        if not self.records:
            return 1
        return max(item.id for item in self.records) + 1

    def add(
        self,
        record_type: str,
        amount: float,
        category: str,
        note: str = "",
        tx_date: str | None = None,
    ) -> Record:
        if record_type not in {"income", "expense"}:
            raise ValueError("type 只能是 income 或 expense")
        if amount <= 0:
            raise ValueError("amount 必须大于 0")

        rec = Record(
            id=self._next_id(),
            type=record_type,
            amount=round(amount, 2),
            category=category,
            note=note,
            date=tx_date or date.today().isoformat(),
        )
        self.records.append(rec)
        self._save()
        return rec

    def delete(self, rec_id: int) -> bool:
        before = len(self.records)
        self.records = [item for item in self.records if item.id != rec_id]
        deleted = len(self.records) < before
        if deleted:
            self._save()
        return deleted

    def list_records(self) -> List[Record]:
        return sorted(self.records, key=lambda x: (x.date, x.id), reverse=True)

    def summary(self) -> dict:
        income = sum(item.amount for item in self.records if item.type == "income")
        expense = sum(item.amount for item in self.records if item.type == "expense")
        balance = round(income - expense, 2)

        category_total = defaultdict(float)
        for item in self.records:
            sign = 1 if item.type == "income" else -1
            category_total[item.category] += sign * item.amount

        return {
            "income": round(income, 2),
            "expense": round(expense, 2),
            "balance": balance,
            "category_total": dict(sorted(category_total.items())),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="记账程序")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="账本文件路径")

    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="新增一条记录")
    add.add_argument("type", choices=["income", "expense"], help="类型")
    add.add_argument("amount", type=float, help="金额")
    add.add_argument("category", help="分类，如 餐饮/工资")
    add.add_argument("--note", default="", help="备注")
    add.add_argument("--date", dest="tx_date", default=None, help="日期，格式 YYYY-MM-DD")

    sub.add_parser("list", help="列出所有记录")

    delete = sub.add_parser("delete", help="删除记录")
    delete.add_argument("id", type=int, help="记录 ID")

    sub.add_parser("summary", help="统计收支")
    return parser


def cmd_add(ledger: Ledger, args: argparse.Namespace) -> int:
    rec = ledger.add(
        record_type=args.type,
        amount=args.amount,
        category=args.category,
        note=args.note,
        tx_date=args.tx_date,
    )
    print(f"已新增：#{rec.id} {rec.date} {rec.type} {rec.amount:.2f} {rec.category} {rec.note}")
    return 0


def cmd_list(ledger: Ledger) -> int:
    items = ledger.list_records()
    if not items:
        print("暂无记录")
        return 0

    print("ID  日期         类型      金额      分类      备注")
    for item in items:
        print(
            f"{item.id:<3} {item.date:<10} {item.type:<8} {item.amount:<8.2f} {item.category:<8} {item.note}"
        )
    return 0


def cmd_delete(ledger: Ledger, rec_id: int) -> int:
    if ledger.delete(rec_id):
        print(f"已删除记录 #{rec_id}")
        return 0
    print(f"未找到记录 #{rec_id}")
    return 1


def cmd_summary(ledger: Ledger) -> int:
    data = ledger.summary()
    print(f"总收入: {data['income']:.2f}")
    print(f"总支出: {data['expense']:.2f}")
    print(f"结余:   {data['balance']:.2f}")
    print("分类净额:")
    if not data["category_total"]:
        print("  (空)")
    for category, amount in data["category_total"].items():
        print(f"  {category}: {amount:.2f}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    ledger = Ledger(db_path=args.db)

    if args.command == "add":
        return cmd_add(ledger, args)
    if args.command == "list":
        return cmd_list(ledger)
    if args.command == "delete":
        return cmd_delete(ledger, args.id)
    if args.command == "summary":
        return cmd_summary(ledger)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
