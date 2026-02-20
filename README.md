# 记账程序（CLI）

这是一个简洁的命令行记账工具，支持：

- 新增收支记录
- 列出所有记录
- 删除指定记录
- 查看汇总统计（收入/支出/结余/分类净额）

## 运行环境

- Python 3.9+

## 使用方式

默认数据文件是当前目录下的 `ledger.json`。

```bash
python3 app.py add expense 28.5 餐饮 --note "午饭"
python3 app.py add income 12000 工资
python3 app.py list
python3 app.py summary
python3 app.py delete 1
```

也可以用 `--db` 指定账本路径：

```bash
python3 app.py --db my_ledger.json add expense 99 购物 --note "耳机"
```

## 数据格式

账本保存在 JSON 文件中，每条记录结构如下：

```json
{
  "id": 1,
  "type": "expense",
  "amount": 28.5,
  "category": "餐饮",
  "note": "午饭",
  "date": "2026-02-20"
}
```
