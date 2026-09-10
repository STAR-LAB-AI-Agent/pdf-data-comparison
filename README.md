# AI PDF 数据比对智能体

一个基于 Python 开源能力的智能体应用实践项目：通过自然语言驱动，比较两份 PDF 文件中的表格数据，自动识别**新增、删除、数值变化**，并输出**变化最大的 Top 5**。

## 项目场景

用户提供两份 PDF（如 2025 年度预算表和 2026 年度预算表），系统自动：
1. 提取 PDF 中的表格数据
2. 清洗为标准 DataFrame
3. 按主键对齐两份数据
4. 识别新增项、删除项、数值变化
5. 计算变化率并输出 Top 5

## 系统架构

```
用户自然语言 → 智能体 → Skill → Python Script/CLI → 开源项目 → 结果
```

- **开源项目**：`tabula-py`（PDF 表格提取）+ `pandas`（数据清洗与比对）
- **Script/CLI**：`scripts/extract_pdf.py`、`scripts/compare_data.py`
- **Skill**：`skills/pdf-compare/SKILL.md`
- **Agent Runtime**：Nanobot

## 安装方法

### 1. 环境要求
- Python 3.10 ~ 3.13
- Java 9+（推荐 Java 17）
- Windows / macOS / Ubuntu

### 2. 创建虚拟环境
```bash
python -m venv .venv
# 或使用 uv（推荐）
uv venv
```

### 3. 激活虚拟环境
- Windows:
  ```powershell
  .\.venv\Scripts\activate
  ```
- macOS / Linux:
  ```bash
  source .venv/bin/activate
  ```

### 4. 安装依赖
```bash
uv pip install -r requirements.txt
```

### 5. 配置 Java 路径
编辑 `scripts/extract_pdf.py` 第一行，将 `JAVA_HOME` 改为你本机的 Java 17 安装路径。

## 运行方法

### 命令行直接比对
```bash
python scripts/compare_data.py data/input/old.pdf data/input/new.pdf 项目名称
```

### 通过 Nanobot 自然语言调用
```bash
nanobot agent -m "帮我比较 old.pdf 和 new.pdf 里各项目的预算变化。"
```

## Skill 使用方式

Skill 说明见 `skills/pdf-compare/SKILL.md`。

核心调用命令：
```bash
python scripts/compare_data.py <旧PDF> <新PDF> <主键列名>
```

## 开源依赖及许可证

| 项目 | 版本 | 许可证 | 用途 |
| :--- | :--- | :--- | :--- |
| tabula-py | 2.10.0 | MIT | 从 PDF 提取表格为 DataFrame |
| pandas | 3.0.5 | BSD-3-Clause | 数据清洗与比对 |
| jpype1 | 1.7.1 | Apache-2.0 | Java-Python 桥接 |
| pytest | 8.3.4 | MIT | 单元测试 |

## 测试方法

```bash
pytest tests/
```

测试覆盖：
- 正常比对（新增、删除、数值变化）
- Top 5 变化排序
- 异常处理（PDF 不存在、无表格、主键缺失）

## 已知问题

- 对扫描型（图片型）PDF 无法提取表格，需先 OCR。
- `tabula-py` 依赖 Java，需确保 Java 9+ 环境正确配置。
- 表格结构极度复杂的 PDF 可能提取失败，建议使用结构清晰的 PDF。

## 项目结构

```
ai-pdf-compare/
├── agent/                  # 智能体层（可选）
├── data/input/             # 测试用 PDF
├── logs/                   # 运行日志
├── scripts/                # 核心 Script/CLI
│   ├── extract_pdf.py
│   └── compare_data.py
├── skills/pdf-compare/     # Skill
│   ├── SKILL.md
│   └── scripts/
├── tests/                  # 测试用例
├── .gitignore
├── README.md
└── requirements.txt
```