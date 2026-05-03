# 参赛提交检查清单（v0.1）

> 依据：2026 年（第十二届）全国大学生统计建模大赛官方通知与《全国大学生统计建模大赛生成式人工智能（AI）工具使用规范（试行）》；本清单用于项目内部收口，不替代学校/赛区最终要求。

## 1. 官方硬性要求跟踪

| 项目 | 当前状态 | 证据/来源 | 下一步 |
| --- | --- | --- | --- |
| 大赛主题 | 已匹配 | 官方主题：“服务国家战略 创新统计赋能” | 标题和摘要继续围绕“双碳 + 数字普惠金融” |
| 论文正文字符数 | 待统计 | 官方通知要求正文字符数（计空格）≤16000 | 最终 Word 版导出后统计 |
| 查重率 | 待完成 | 官方通知要求查重率≤20%，超过40%视为学术不端 | 论文定稿后做知网查重 |
| AI 工具使用情况表 | 待用户/队伍填写 | 官方通知列为参赛材料；AI 使用规范要求披露并保留必要材料 | 根据实际使用 Codex/Claude/LLM 情况如实填写 |
| 承诺书 | 待用户/队伍填写 | 官方通知列为参赛材料 | 使用大赛附件模板 |
| 报名表 | 待用户/队伍填写 | 官方通知列为参赛材料 | 使用大赛附件模板 |
| 论文 | v0.2 初稿完成 | `docs/paper/03_manuscript_v0_2.md` | 转 Word/排版/压缩字数 |
| 数据包 | 部分就绪 | `data/raw/`, `data/interim/`, `outputs/` | 整理可公开提交版本，剔除不应提交的原始授权数据 |
| 代码包 | 基本就绪 | `src/`, `tests/`, `README.md`, `environment.yml` | 最终重跑并写运行说明 |

## 2. 论文定稿任务

- [ ] 将 `docs/paper/03_manuscript_v0_2.md` 转成 Word 正式稿，并由参赛队人工审阅、改写和确认正文表述。
- [ ] 统一标题、摘要、关键词、一级/二级标题格式。
- [ ] 将正文表图编号与 `docs/paper/table-figure-inventory.md` 对齐。
- [ ] 决定 Table 5 / Figure 4 / Table 13 是否全部放入技术附录。
- [ ] 将 Table 9 定位为答辩/结论汇总，不替代模型结果表。
- [ ] 补齐参考文献格式，至少覆盖 `docs/paper/references.md` 与 `docs/paper/references.bib` 中的核心文献。
- [ ] 明确“DML 不能自动解决所有内生性”的识别边界。
- [ ] 明确人口变量敏感性边界：人口不进主回归，Table 11 必须披露。
- [ ] 明确政策文本边界：Table 13 当前为 `not_ready`，不能写成最终 LLM 机制证据。

## 3. 表图与输出任务

- [x] 本轮重跑所有表图生成脚本（2026-05-03）：
  ```bash
  python3 src/03_eda.py
  python3 src/06_robustness.py
  python3 src/28_export_population_sensitivity.py
  python3 src/27_export_heterogeneity_groups.py
  python3 src/29_export_heterogeneity_group_differences.py
  python3 src/30_prepare_policy_llm_scoring_batch.py
  python3 src/31_validate_policy_llm_scores.py
  python3 src/26_export_evidence_synthesis.py
  python3 src/25_export_result_figures.py
  ```
- [x] 检查 `outputs/tables/*.tex` 是否满足三线表要求（`booktabs` 结构已存在）。
- [x] 检查 `outputs/figures/*.pdf` 是否可正常识别为 PDF（当前合同图件均为 1 页 PDF）。
- [ ] 决定是否将最终表图从 ignored outputs 中 force-add 到提交包或单独压缩。

## 4. 数据与代码包任务

- [ ] 确认 `data/raw/` 中哪些文件可提交，哪些受授权限制只能在说明中描述。
- [ ] 准备 `data/processed/` 或最小可复现输入表，避免提交过大的中间文件。
- [ ] 补充数据来源说明：PKU 指数、CMCC、控制变量来源。
- [x] 使用 `python3 src/32_prepare_submission_package.py` 生成本地提交包；默认不复制 `data/raw/`。
- [ ] 若确认派生数据可提交，再使用 `python3 src/32_prepare_submission_package.py --include-derived-data` 生成含派生数据版本。
- [ ] 运行完整测试：`python3 -m pytest -q`。
- [ ] 运行语法检查：`python3 -m py_compile $(find src tests -name '*.py' | sort)`。
- [ ] 确认 `README.md` 中运行顺序与当前脚本一致。
- [ ] 导出环境说明：`environment.yml` 或 `requirements` 与实际运行环境一致。

## 5. AI 使用声明草案

当前项目开发过程中使用了 AI 编码/写作辅助工具协助：

- 项目结构设计与代码实现辅助；
- Python 数据处理、建模、表图导出脚本编写；
- 论文初稿结构和文字草拟；
- 政策文本 LLM scoring 框架设计；
- Git 管理和验证流程执行。

正式填写 AI 工具使用情况表时应遵循大赛附件格式和 AI 使用规范，并由参赛队确认以下内容：

- 哪些文本为 AI 辅助生成后人工审阅修改；
- 哪些代码由 AI 辅助生成并经测试验证；
- 是否使用真实 LLM 对政策文本进行评分；
- 是否保留 AI 工具调用记录、提示词或模型版本说明。
- 最终提交论文正文不得直接以 AI 原始输出替代人工论文写作，应保留人工审阅、改写和责任确认痕迹。

## 6. 当前最短冲刺路径

1. 先把 `03_manuscript_v0_2.md` 转成 Word 初稿，并进行人工改写确认。
2. 按 Table/Figure inventory 插入正文表图占位。
3. 统一参考文献格式。
4. 做一次最终重跑和测试。
5. 用 `src/32_prepare_submission_package.py` 生成本地提交包。
6. 完成 AI 使用表、承诺书、报名表、查重报告。
7. 整理最终代码包和数据包。
