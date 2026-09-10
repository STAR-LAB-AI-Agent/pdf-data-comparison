import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from extract_pdf import clean_extracted_table


def test_clean_standard_table():
    """测试标准表格清洗"""
    raw = pd.DataFrame({
        0: ["学号", "12", "32"],
        1: ["姓名", "张三", "李四"],
        2: ["成绩", "100", "98"],
    })
    df = clean_extracted_table(raw)
    assert list(df.columns) == ["学号", "姓名", "成绩"]
    assert len(df) == 2


def test_clean_with_empty_columns():
    """测试带空列的表格清洗"""
    raw = pd.DataFrame({
        0: ["项目名称", "社区打扫"],
        1: ["人数", "5"],
        2: [None, None],
        3: ["预算", "500"],
    })
    df = clean_extracted_table(raw)
    assert "项目名称" in df.columns
    assert "预算" in df.columns