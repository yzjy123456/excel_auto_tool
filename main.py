# main.py
import logging
from pathlib import Path
import pandas as pd
from config import *

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def init_folder():
    """初始化输入输出文件夹，不存在就自动创建"""
    Path(INPUT_FOLDER).mkdir(exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)


def read_all_excel() -> list:
    """批量读取input文件夹下所有xlsx，返回df列表"""
    df_list = []
    file_list = list(Path(INPUT_FOLDER).glob("*.xlsx"))
    if len(file_list) == 0:
        logger.warning("input文件夹下没有找到xlsx文件！")
        return df_list

    for fp in file_list:
        try:
            logger.info(f"正在读取：{fp.name}")
            df = pd.read_excel(fp, engine="openpyxl")
            df_list.append(df)
        except Exception as e:
            logger.error(f"读取文件 {fp.name} 失败：{str(e)}")
    return df_list


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """单表清洗逻辑"""
    df = df.copy()
    # 文本去空格
    if TRIM_STR:
        for col in df.select_dtypes(include=["object", "str", "string"]).columns:
            df[col] = df[col].astype(str).str.strip()

    # 删除全空行
    if DROP_EMPTY_ROW:
        df = df.dropna(how="all")

    # 空值处理：按列类型区分——文本列填"未知"，数值列填0（避免类型混乱导致求和报错）
    if FILL_NA_METHOD == "zero":
        df = df.fillna(0)
    elif FILL_NA_METHOD == "unknown":
        for col in df.columns:
            dtype = df[col].dtype.name
            if dtype.startswith("str") or dtype == "object":
                df[col] = df[col].fillna("未知")
            else:
                df[col] = df[col].fillna(0)
    elif FILL_NA_METHOD == "drop":
        df = df.dropna()

    # 指定列去重
    if DROP_DUPLICATE_COL is not None and DROP_DUPLICATE_COL in df.columns:
        df = df.drop_duplicates(subset=[DROP_DUPLICATE_COL], keep="first")

    return df


def generate_summary(df: pd.DataFrame) -> pd.DataFrame:
    """生成分组汇总统计表"""
    if GROUP_BY_COL not in df.columns or SUM_COL not in df.columns:
        logger.warning("分组列/求和列不存在，跳过汇总！")
        return pd.DataFrame()
    summary = df.groupby(GROUP_BY_COL, as_index=False)[SUM_COL].agg(["count", "sum"])
    summary.columns = [GROUP_BY_COL, "数量", "总和"]
    return summary


def main():
    init_folder()
    df_list = read_all_excel()
    if not df_list:
        logger.info("无数据，程序退出")
        return

    # 合并所有表 + 清洗
    all_df = pd.concat(df_list, ignore_index=True)
    clean_df = clean_data(all_df)
    summary_df = generate_summary(clean_df)

    # 导出
    clean_path = Path(OUTPUT_FOLDER) / "cleaned_data.xlsx"
    summary_path = Path(OUTPUT_FOLDER) / "summary_report.xlsx"
    clean_df.to_excel(clean_path, index=False, engine="openpyxl")
    summary_df.to_excel(summary_path, index=False, engine="openpyxl")

    logger.info(f"清洗完成！明细输出：{clean_path}")
    logger.info(f"汇总报表输出：{summary_path}")


if __name__ == "__main__":
    main()
