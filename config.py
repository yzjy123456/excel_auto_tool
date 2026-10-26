# config.py 配置项，用户在这里修改规则
# ---------------------- 路径配置 ----------------------
INPUT_FOLDER = "./input"
OUTPUT_FOLDER = "./output"

# ---------------------- 清洗规则 ----------------------
DROP_EMPTY_ROW = True          # 是否删除全空行
DROP_DUPLICATE_COL = "name"    # 根据哪一列去重，不需要去重填 None
FILL_NA_METHOD = "unknown"     # 空值处理："zero"填0 / "unknown"填未知 / "drop"删除该行
TRIM_STR = True                # 文本去除首尾空格

# ---------------------- 统计规则 ----------------------
GROUP_BY_COL = "department"    # 按哪一列分组统计
SUM_COL = "amount"             # 需要求和的列
