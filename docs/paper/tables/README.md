# 论文表格（CSV / LaTeX 版）

本目录保存论文表格的 CSV 与 LaTeX 版本，用于 GitHub 协作审阅、论文排版和结果核对。

- 原始生成目录：`outputs/tables/`（默认被 `.gitignore` 忽略）
- 主要生成脚本：`src/03_eda.py`、`src/06_robustness.py`、`src/14_export_table_02.py`、`src/15_export_table_03.py`、`src/16_export_table_04.py`、`src/24_export_table_05.py`、`src/26_export_evidence_synthesis.py`、`src/27_export_heterogeneity_groups.py`、`src/28_export_population_sensitivity.py`、`src/29_export_heterogeneity_group_differences.py`、`src/31_validate_policy_llm_scores.py`、`src/34_export_paper_support_materials.py`
- 若样本、变量或模型规格变化，应先重新运行生成脚本，再同步刷新本目录。

## 表格内容

- `table_01_*`：描述性统计
- `table_02_*`：DML 主结果与替换结果变量
- `table_03_*`：CATE 技术摘要
- `table_04_*`：CATE 城市极值诊断
- `table_05_*`：政策文本 seed 机制候选
- `table_06_*`：OLS 双向固定效应对照
- `table_07_*`：DML 安慰剂检验摘要与置换分布
- `table_08_*`：DML 学习器替换检验
- `table_09_*`：当前证据链汇总
- `table_10_*`：异质性分组摘要
- `table_11_*`：人口变量敏感性
- `table_12_*`：异质性组间差异诊断
- `table_13_*`：政策文本 LLM 验证就绪度
- `table_14_*`：样本构造与覆盖情况
- `table_15_*`：主要变量相关系数矩阵
