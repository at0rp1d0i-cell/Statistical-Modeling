# 参考文献与资料来源清单（v0.1）

> 目的：为 `docs/paper/03_manuscript_v0_2.md` 提供可追溯参考文献底稿。正式提交前仍需按学校/大赛要求统一为目标引用格式，并逐条核对作者、题名、卷期、页码、DOI 和访问日期。

## 一、方法与识别文献

1. Chernozhukov, V., Chetverikov, D., Demirer, M., Duflo, E., Hansen, C., Newey, W., & Robins, J. (2018). Double/debiased machine learning for treatment and structural parameters. *The Econometrics Journal*, 21(1), C1–C68. https://doi.org/10.1111/ectj.12097
   - 用途：DML 方法基础；支持正交化、交叉拟合和部分线性 DML 的识别表述。

2. Wager, S., & Athey, S. (2018). Estimation and inference of heterogeneous treatment effects using random forests. *Journal of the American Statistical Association*, 113(523), 1228–1242. https://doi.org/10.1080/01621459.2017.1319839
   - 用途：因果森林/随机森林异质性处理效应估计基础。

3. Athey, S., Tibshirani, J., & Wager, S. (2019). Generalized random forests. *The Annals of Statistics*, 47(2), 1148–1178. https://doi.org/10.1214/18-AOS1709
   - 用途：广义随机森林方法基础；支持 CATE 与异质性估计。

## 二、数字普惠金融与碳减排相关文献

4. 郭峰、王靖一、王芳、孔涛、张勋、程志云（2020）：《测度中国数字普惠金融发展：指数编制与空间特征》，《经济学（季刊）》第 19 卷第 4 期。
   - 用途：北京大学数字普惠金融指数的核心引用。北京大学数字金融研究中心要求使用指数时注明“北京大学数字普惠金融指数”并引用该文献。

5. Zhao, H., Chen, S., & Zhang, W. (2023). Does digital inclusive finance affect urban carbon emission intensity: Evidence from 285 cities in China. *Cities*, 142, 104552. https://doi.org/10.1016/j.cities.2023.104552
   - 用途：直接支持“数字普惠金融—城市碳排放强度”研究组合；样本为中国城市面板。

6. Su, Z., & Cao, R. (2023). Impact of digital inclusive finance on urban carbon emission intensity: From the perspective of green and low-carbon travel and clean energy. *Sustainability*, 15(16), 12623. https://doi.org/10.3390/su151612623
   - 用途：支持数字普惠金融降低城市碳排放强度，以及西部、低经济发展水平城市可能存在更强效应的异质性叙述。

7. Lu, Y., & Xia, Z. (2024). Digital inclusive finance, green technological innovation, and carbon emissions from a spatial perspective. *Scientific Reports*, 14, 8454. https://doi.org/10.1038/s41598-024-59081-9
   - 用途：支持数字普惠金融、绿色技术创新、空间溢出和碳排放机制讨论。

## 三、数据与指标来源

8. 北京大学数字金融研究中心：北京大学数字普惠金融指数（2011–2023）。https://idf.pku.edu.cn/
   - 用途：本文处理变量来源。当前本地数据文件为 `data/raw/2026-04-13_统计建模数据/北大数字普惠金融指数/北京大学数字普惠金融指数（PKU-DFIIC）2011-2023.xlsx`。

9. CMCC 城市碳排放数据（本地归档）：`data/raw/2026-04-13_统计建模数据/2019-2024 china_city_data_all.csv`。
   - 用途：当前碳排放总量与碳排放强度构造来源。正式提交前需按数据提供方/下载页面补齐公开引用或数据说明。

10. 城市核心控制变量数据（本地归档）：详见 `data/interim/modeling/modeling_candidate_panel_2019_2023.csv` 与相关脚本。
    - 用途：地区生产总值、第二产业占比、财政支出、人口候选变量等。正式提交前需按原始年鉴/EPS/CEIC/Wind 或实际数据来源补齐引用。

## 四、政策文本与竞赛规范来源

11. 中国统计教育学会（2026）：《关于举办 2026 年（第十二届）全国大学生统计建模大赛的通知》。https://www.cmathc.org.cn/mcm/tz/412.html
    - 用途：大赛主题、参赛材料、字数、查重、AI 使用情况表等提交规范来源。

12. 全国大学生统计建模大赛组委会（2026）：《全国大学生统计建模大赛生成式人工智能（AI）工具使用规范（试行）》。https://www.cmathc.org.cn/mcm/news/416.html
    - 用途：AI 工具使用边界、披露、原始数据/代码/交互日志留存、论文正文不得直接由 AI 生成等合规要求来源。

13. 政策文本 seed 文档：详见 `data/interim/policy_text/policy_document_registry_seed_central.csv`。
    - 用途：政策文本机制模块当前 seed 语料。正式提交前若扩展完整语料，需从 registry 自动导出正式政策文件引用表。

## 五、仍需补齐的引用缺口

- CMCC 城市碳排放数据的公开说明或数据提供方引用。
- 控制变量原始来源（统计年鉴、EPS、CEIC、Wind 或其他实际来源）。
- 政策文本完整语料（若执行真实 LLM scoring）对应的中央、省级、地级市政策文件引用。
- 若最终保留政策文本 LLM 模块，需要补充 LLM 评分模型、调用日期、人工复核方案、交互日志留存方式与 AI 使用声明。
