import pandas as pd

from stat_modeling.config import TABLES_DIR


SOURCE = TABLES_DIR / "table_05_policy_seed_mechanism_candidate.csv"
TARGET = TABLES_DIR / "table_05_policy_seed_mechanism_candidate.tex"

VARIABLE_LABELS = {
    "sum_policy_strength_city_year": "政策强度（city-year 汇总）",
    "mean_execution_clarity_city_year": "执行明确性（city-year 均值）",
    "mean_digital_green_synergy_city_year": "数字绿色协同度（city-year 均值）",
}


def main() -> int:
    frame = pd.read_csv(SOURCE)
    display = frame[
        [
            "variable_name",
            "coefficient",
            "std_error",
            "ci_lower",
            "ci_upper",
            "p_value",
            "nobs",
        ]
    ].copy()
    display["variable_name"] = display["variable_name"].map(VARIABLE_LABELS).fillna(display["variable_name"])
    display.columns = [
        "机制候选变量",
        "系数",
        "标准误",
        "95%CI下限",
        "95%CI上限",
        "P值",
        "样本量",
    ]
    for column in ["系数", "标准误", "95%CI下限", "95%CI上限", "P值"]:
        display[column] = display[column].map(lambda x: f"{x:.4f}")
    display["样本量"] = display["样本量"].astype(int).astype(str)
    latex = display.to_latex(
        index=False,
        escape=False,
        caption="政策文本 seed 机制候选结果（规则代理，非最终机制结论）",
        label="tab:policy_seed_mechanism_candidate",
    )
    TARGET.write_text(latex, encoding="utf-8")
    print(f"LaTeX table written to: {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
