import pandas as pd
import sys
from pathlib import Path

# 把 scripts 目录加入路径
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from compare_data import compare_dataframes, get_top_changes


def test_added():
    old_df = pd.DataFrame({"项目名称": ["A", "B"], "预算": [100, 200]})
    new_df = pd.DataFrame({"项目名称": ["A", "B", "C"], "预算": [100, 200, 300]})
    result = compare_dataframes(old_df, new_df, "项目名称")
    assert len(result["added"]) == 1
    assert result["added"][0]["项目名称"] == "C"


def test_removed():
    old_df = pd.DataFrame({"项目名称": ["A", "B"], "预算": [100, 200]})
    new_df = pd.DataFrame({"项目名称": ["A"], "预算": [100]})
    result = compare_dataframes(old_df, new_df, "项目名称")
    assert len(result["removed"]) == 1
    assert result["removed"][0]["项目名称"] == "B"


def test_changed():
    old_df = pd.DataFrame({"项目名称": ["A"], "预算": [100]})
    new_df = pd.DataFrame({"项目名称": ["A"], "预算": [150]})
    result = compare_dataframes(old_df, new_df, "项目名称")
    assert len(result["changed"]) == 1
    assert result["changed"][0]["delta"] == 50
    assert result["changed"][0]["rate"] == 0.5


def test_top_changes():
    changed = [
        {"key": "A", "column": "预算", "old_value": 100, "new_value": 200, "delta": 100, "rate": 1.0},
        {"key": "B", "column": "预算", "old_value": 100, "new_value": 50, "delta": -50, "rate": -0.5},
        {"key": "C", "column": "预算", "old_value": 100, "new_value": 110, "delta": 10, "rate": 0.1},
    ]
    top = get_top_changes(changed, top_n=2)
    assert len(top) == 2
    assert top[0]["key"] == "A"
    assert top[1]["key"] == "B"


def test_missing_key_column():
    old_df = pd.DataFrame({"项目名称": ["A"], "预算": [100]})
    new_df = pd.DataFrame({"项目名称": ["A"], "预算": [150]})
    try:
        compare_dataframes(old_df, new_df, "不存在的列")
        assert False, "应该抛出 ValueError"
    except ValueError:
        pass