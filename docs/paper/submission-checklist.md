# 参赛提交检查清单（v0.2）

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
| 论文 | 投稿候选稿完成 | `docs/paper/04_submission_manuscript_candidate.md`；本地 DOCX 可由 `src/33_export_submission_docx.py` 生成；最终编辑指南见 `docs/paper/final-editing-guide.md` | 按指南排版/压缩字数/人工改写 |
| 数据包 | 部分就绪 | `data/raw/`, `data/interim/`, `outputs/` | 整理可公开提交版本，剔除不应提交的原始授权数据 |
| 代码包 | 基本就绪 | `src/`, `tests/`, `README.md`, `environment.yml` | 最终重跑并写运行说明 |

## 2. 论文定稿任务

- [ ] 将 `docs/paper/04_submission_manuscript_candidate.md` 转成 Word 正式稿，并由参赛队人工审阅、改写和确认正文表述。
- [x] 建立最终 Word 编辑指南：`docs/paper/final-editing-guide.md`（规定正文/附录表图放置、编辑顺序和不可过度宣称边界）。
- [x] 生成本地 Word 初稿：`python3 src/33_export_submission_docx.py`（默认仅追加核心表格摘录：表1、表2、表7、表10、表11、表14；完整表1—15保留在 `outputs/tables/`；同时追加图1—10图件清单，图件提供 PDF/PNG/JPG，供 Word/WPS 内移动到正文）。
- [ ] 统一标题、摘要、关键词、一级/二级标题格式。
- [x] 完成往届优秀论文写作风格审读备忘录：`docs/paper/06_prior_winner_style_review.md`。
- [x] 新增研究框架与技术路线图 Figure 10，便于对齐获奖论文常见“研究思路/框架结构”写法。
- [ ] 按 `docs/paper/final-editing-guide.md` 移动正文表图，并将正文表图编号与 `docs/paper/table-figure-inventory.md` 对齐。
- [x] 当前放置建议已确认：正文优先 Table 1/2/6/7/8/10/11/12/14 与 Figure 10/1/2/5/6/7/8；技术附录放 Table 3/4/5/9/13/15 与 Figure 3/4/9。
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
  python3 src/34_export_paper_support_materials.py
  ```
- [x] 检查 `outputs/tables/*.tex` 是否满足三线表要求（`booktabs` 结构已存在）。
- [x] 检查 `outputs/figures/*.pdf` 是否可正常识别为 PDF（当前合同图件 Figure 1—10 均生成 PDF/PNG/JPG）。
- [x] 当前图件导出链路同时生成 PNG/JPG，便于 Word/WPS 插图；新增 Table 14/15 与 Figure 7/8/9/10 作为论文支撑素材。
- [x] 当前提交包脚本会复制 ignored `outputs/tables/` 与 `outputs/figures/` 生成物到本地 `dist/submission_package_current/`，无需 force-add 到 Git。

## 4. 数据与代码包任务

- [ ] 确认 `data/raw/` 中哪些文件可提交，哪些受授权限制只能在说明中描述。
- [ ] 准备 `data/processed/` 或最小可复现输入表，避免提交过大的中间文件。
- [ ] 补充数据来源说明：PKU 指数、CMCC、控制变量来源。
- [x] 使用 `python3 src/32_prepare_submission_package.py` 生成本地提交包；默认不复制 `data/raw/`。
- [x] 本地提交包自动包含 `paper/final-editing-guide.md`、`paper/05_materials_and_adversarial_review.md` 和 `paper/04_submission_manuscript_candidate.docx`，DOCX 文末仅附核心表格摘录与图件清单；完整表格在提交包 `outputs/tables/` 中保留。
- [ ] 若确认派生数据可提交，再使用 `python3 src/32_prepare_submission_package.py --include-derived-data` 生成含派生数据版本。
- [x] 运行完整测试：`python3 -m pytest -q`（2026-05-04，95 passed）。
- [x] 运行语法检查：`python3 -m py_compile $(find src tests -name '*.py' | sort)`（2026-05-04，exit 0）。
- [x] 确认 `README.md` 中运行顺序与当前脚本一致（已包含 `src/34_export_paper_support_materials.py`）。
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

1. 先阅读 `docs/paper/final-editing-guide.md`，再打开 `dist/04_submission_manuscript_candidate.docx` 或提交包内 `paper/04_submission_manuscript_candidate.docx`，进行人工改写确认。
2. 按 final editing guide 和 Table/Figure inventory 插入正文表图占位。
3. 统一参考文献格式。
4. 做一次最终重跑和测试。
5. 用 `src/32_prepare_submission_package.py` 生成本地提交包。
6. 完成 AI 使用表、承诺书、报名表、查重报告。
7. 整理最终代码包和数据包。
