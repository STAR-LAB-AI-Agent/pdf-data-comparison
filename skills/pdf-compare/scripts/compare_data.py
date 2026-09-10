import os
os.environ['JAVA_HOME'] = "C:\\Program Files\\Microsoft\\jdk-17.0.20.101-hotspot"

from pathlib import Path
import sys
import pandas as pd
from extract_pdf import extract_tables, clean_extracted_table


def load_pdf_as_dataframe(pdf_path: str) -> pd.DataFrame:
    """加载 PDF 并返回清洗后的 DataFrame"""
    tables = extract_tables(pdf_path)
    if not tables:
        raise ValueError(f"PDF 中未提取到表格: {pdf_path}")
    df = clean_extracted_table(tables[0])
    return df


def compare_dataframes(
    old_df: pd.DataFrame,
    new_df: pd.DataFrame,
    key_column: str
) -> dict:
    """
    比对两个 DataFrame，识别新增、删除、数值变化。

    Args:
        old_df: 旧版数据
        new_df: 新版数据
        key_column: 主键列名（如 '项目名称' 或 '学号'）

    Returns:
        dict: {
            'added': 新增数据列表,
            'removed': 删除数据列表,
            'changed': 变化详情列表 (每条包含 key, column, old_value, new_value, delta, rate)
        }
    """
    # 检查主键是否存在
    if key_column not in old_df.columns:
        raise ValueError(f"旧数据中不存在主键列: {key_column}")
    if key_column not in new_df.columns:
        raise ValueError(f"新数据中不存在主键列: {key_column}")

    # 复制数据避免修改原数据
    old_df = old_df.copy()
    new_df = new_df.copy()

    # 确保主键列为字符串类型，便于比较
    old_df[key_column] = old_df[key_column].astype(str).str.strip()
    new_df[key_column] = new_df[key_column].astype(str).str.strip()

    # 获取主键集合
    old_keys = set(old_df[key_column])
    new_keys = set(new_df[key_column])

    # 新增：新有旧无
    added_keys = new_keys - old_keys
    removed_keys = old_keys - new_keys
    common_keys = old_keys & new_keys

    # 提取新增数据
    added = new_df[new_df[key_column].isin(added_keys)]

    # 提取删除数据
    removed = old_df[old_df[key_column].isin(removed_keys)]

    # ---- 变化分析 ----
    changed = []

    # 按主键建立索引
    old_index = old_df.set_index(key_column)
    new_index = new_df.set_index(key_column)

    # 找出所有数值列（尝试转为数字，成功则为数值列）
    numeric_columns = []
    for col in old_df.columns:
        if col == key_column:
            continue
        # 检查该列是否在 new 中存在
        if col not in new_df.columns:
            continue
        # 尝试转为数字
        try:
            pd.to_numeric(old_df[col], errors='raise')
            pd.to_numeric(new_df[col], errors='raise')
            numeric_columns.append(col)
        except (ValueError, TypeError):
            # 该列不是纯数字，跳过（如 '姓名' 列）
            pass

    # 对每个共同主键，比较数值列的变化
    for key in common_keys:
        old_row = old_index.loc[key]
        new_row = new_index.loc[key]

        for col in numeric_columns:
            old_val = old_row[col]
            new_val = new_row[col]

            # 如果两个都是 NaN，跳过
            if pd.isna(old_val) and pd.isna(new_val):
                continue

            # 转成 float 以便计算
            try:
                old_num = float(old_val)
                new_num = float(new_val)
            except (ValueError, TypeError):
                continue

            # 如果有变化
            if old_num != new_num:
                delta = new_num - old_num
                rate = None
                if old_num != 0:
                    rate = delta / old_num
                changed.append({
                    'key': key,
                    'column': col,
                    'old_value': old_num,
                    'new_value': new_num,
                    'delta': delta,
                    'rate': rate
                })

    return {
        'added': added.to_dict(orient='records'),
        'removed': removed.to_dict(orient='records'),
        'changed': changed
    }


def get_top_changes(changed: list, top_n: int = 5) -> list:
    """
    从变化列表中提取变化率绝对值最大的前 N 项。
    """
    # 过滤掉 rate 为 None 的项
    numeric_changes = [item for item in changed if item['rate'] is not None]

    # 按绝对值排序
    numeric_changes.sort(key=lambda x: abs(x['rate']), reverse=True)

    return numeric_changes[:top_n]


def format_result(result: dict, top_n: int = 5) -> str:
    """将比对结果格式化为可读文本"""
    lines = []

    added_count = len(result['added'])
    removed_count = len(result['removed'])
    changed_count = len(result['changed'])

    lines.append(f"📊 数据比对结果")
    lines.append(f"   - 新增：{added_count} 项")
    lines.append(f"   - 删除：{removed_count} 项")
    lines.append(f"   - 变化：{changed_count} 项")

    if result['added']:
        lines.append(f"\n🆕 新增数据：")
        for item in result['added']:
            lines.append(f"   {item}")

    if result['removed']:
        lines.append(f"\n❌ 删除数据：")
        for item in result['removed']:
            lines.append(f"   {item}")

    if result['changed']:
        lines.append(f"\n📈 数值变化：")
        top = get_top_changes(result['changed'], top_n)
        for item in top:
            rate_str = f"{item['rate']:.1%}" if item['rate'] is not None else "N/A"
            lines.append(f"   {item['key']} 的 {item['column']}: {item['old_value']} → {item['new_value']} (变化: {rate_str})")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python compare_data.py old.pdf new.pdf 主键列名")
        print("示例: python compare_data.py old.pdf new.pdf 项目名称")
        print("示例: python compare_data.py old.pdf new.pdf 学号")
        sys.exit(1)

    old_pdf = sys.argv[1]
    new_pdf = sys.argv[2]
    key_column = sys.argv[3]

    try:
        print("📖 读取 PDF 文件...")
        old_df = load_pdf_as_dataframe(old_pdf)
        new_df = load_pdf_as_dataframe(new_pdf)

        print(f"📋 旧数据: {len(old_df)} 行, 列: {list(old_df.columns)}")
        print(f"📋 新数据: {len(new_df)} 行, 列: {list(new_df.columns)}")
        print(f"🔑 主键列: {key_column}")

        print("\n🔄 开始比对...")
        result = compare_dataframes(old_df, new_df, key_column)

        print("\n" + format_result(result, top_n=5))

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        sys.exit(1)