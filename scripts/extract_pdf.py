import os
os.environ['JAVA_HOME'] = "C:\\Program Files\\Microsoft\\jdk-17.0.20.101-hotspot"

from pathlib import Path
import sys
import tabula
import pandas as pd
import numpy as np


def extract_tables(pdf_path: str):
    """提取 PDF 表格"""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF不存在: {pdf_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("输入文件必须是PDF")
    tables = tabula.read_pdf(
        str(path),
        pages=1,
        multiple_tables=True,
        lattice=False,
        stream=True,
        guess=True,
        pandas_options={'header': None}
    )
    tables = [df for df in tables if not df.empty]
    return tables


def clean_extracted_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    通用清洗函数，不做类型转换，只做结构整理。
    1. 删除全空列
    2. 第一行作为列名
    3. 删除第一行（原表头数据）
    4. 清理列名中的前后空格
    5. 重置索引
    """
    # 删除全空列
    df = df.dropna(axis=1, how='all')
    if df.empty:
        return df

    # 第一行作为列名
    new_header = df.iloc[0].tolist()
    # 将列名中的 NaN 替换为 "列N"
    col_names = []
    for i, val in enumerate(new_header):
        if pd.isna(val) or str(val).strip() == '':
            col_names.append(f"列{i+1}")
        else:
            col_names.append(str(val).strip())
    df.columns = col_names

    # 删除第一行（原表头行）
    df = df.iloc[1:].reset_index(drop=True)

    # 注意：不在此处转换数据类型，保留原始字符串格式，后续按需转换
    return df


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python extract_pdf.py xxx.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    try:
        tables = extract_tables(pdf_path)

        if tables:
            tables = [clean_extracted_table(df) for df in tables]

        if tables:
            print(f"\n✅ 成功提取 {len(tables)} 个表格")
            for i, df in enumerate(tables, start=1):
                print(f"\n===== 表格 {i} =====")
                print(df.to_string(index=False))
        else:
            print("❌ 未能提取到任何表格")

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        sys.exit(1)