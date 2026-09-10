---
name: pdf-compare
description: "比较两份 PDF 文件中的表格数据，识别新增、删除和数值变化。当用户要求对比两个 PDF 文件、查看数据变化、找出变化最大的项目时，应该使用此技能。"
---

# PDF 数据比对技能

## 功能说明
此技能用于比较两份 PDF 文件中的表格数据，自动识别新增、删除、数值变化，并计算变化率，输出变化最大的前 5 项。底层使用 `tabula-py` 提取 PDF 表格，使用 `pandas` 进行数据清洗与比对。

## 使用场景
- 用户需要对比两个版本的财务报表、预算表或成绩单。
- 用户想知道哪些数据被删除了，哪些是新增的。
- 用户想快速找出变化幅度最大的项目。

## 调用方式
在技能根目录下执行以下命令：
```bash
python scripts/compare_data.py <旧文件路径> <新文件路径> <主键列名>
```

> **说明**：脚本位于本技能目录下的 `scripts/` 文件夹中。如果 Agent 的工作目录不在技能根目录，请先 `cd` 到技能目录，或使用绝对路径调用脚本。

## 参数说明
| 参数 | 类型 | 必填 | 示例 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `old_pdf` | 字符串 | 是 | `data/input/old.pdf` | 旧版 PDF 文件路径 |
| `new_pdf` | 字符串 | 是 | `data/input/new.pdf` | 新版 PDF 文件路径 |
| `key_column` | 字符串 | 是 | `项目名称` | 用于匹配两表数据的唯一主键列名（如“项目名称”“学号”） |

## 输出格式
脚本返回结构化的文本结果，包含：
- 📊 概览（新增/删除/变化数量）
- 🆕 新增数据列表
- ❌ 删除数据列表
- 📈 Top 5 变化项（含变化率）

## 使用示例

**示例 1：比较预算表变化**
用户输入：
> “帮我比较 `old.pdf` 和 `new.pdf` 里各项目的预算变化。”

技能执行：
```bash
python scripts/compare_data.py data/input/old.pdf data/input/new.pdf 项目名称
```

**示例 2：比较成绩表变化**
用户输入：
> “比较两个成绩单，用学号作为主键，看看成绩和排名有什么变化。”

技能执行：
```bash
python scripts/compare_data.py data/input/old.pdf data/input/new.pdf 学号
```

## 依赖与环境要求
- Python 3.10 ~ 3.13
- 依赖包：`tabula-py`、`pandas`、`jpype1`
- 需要 Java 9 或更高版本（推荐 Java 17）。本技能脚本已在开头通过 `os.environ['JAVA_HOME']` 指定 Java 17 路径，如你的环境不同，请修改脚本中的 `JAVA_HOME` 值。
- 安装依赖：
  ```bash
  uv pip install tabula-py pandas jpype1
  ```