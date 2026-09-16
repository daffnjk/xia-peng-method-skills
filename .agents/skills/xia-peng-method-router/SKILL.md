---
name: xia-peng-method-router
description: 路由夏鹏智能体方法论与职业规划任务；覆盖个性化、场景型 Skill、目标管理、多 Agent、副业验证和职业/生涯选择。
version: 0.3.4
---

先读取并遵守 `03_agent/METHOD_POLICY.md`，包括直接显式调用本 Skill 的情况。依赖与可选辅助能力见 `03_agent/skill_registry.json`。这是方法流程，不代表已执行任何工具动作。

复合任务只选一个主 Skill，按 `03_agent/skill_registry.json` 补必要辅助能力；复用已授权上下文，禁止无界递归和重复画像收集。

# 目标

判断用户请求属于哪个方法模块，并确保不超出manifest登记来源的证据边界。

# 路由

1. 个人资料与“懂我” → `understand-me`
2. 把工作方法做成 Skill → `scene-skill-builder`
3. 目标拆解、资源、汇报、复盘 → `goal-management`
4. 多 Agent 角色与闭环 → `agent-team-workflow`
5. 副业候选、评估、执行 → `side-business-system`
6. 优势识别、岗位匹配、跳槽/转行、offer/行业/公司/城市/学历决策、第二曲线 → `career-planning`
7. 带团队、KPI/OKR 选择、团队会议、绩效面谈、授权与激励、新接团队 → `minimalist-management`（来源《极简管理课》已入库，含段落锚点但 assurance 为 location_checked_not_semantic_verification；个人目标拆解仍归 `goal-management`）
8. 询问材料原意 → 检索对应原始记录、视觉阅读记录和知识卡
9. 其他夏鹏观点 → 明确“材料不足”，不得外推成完整人格

# 来源规则

- 明确表达、材料归纳、工程化外推必须分开。
- 任何“夏鹏认为”按公共规则给来源 ID 与真实文件路径；不得补造锚点。
- 不使用讲者的贬损、竞品攻击、价格与课程销售话术。
- XP-T-004 中的公司、行业、城市、薪资、学历和平台例子是录制时材料；当前决策需重新核验。
- 人格/兴趣测评、年限、能力百分位和收入公式只能作启发，不得作确定性诊断或承诺。

## 外部书籍知识检索：刘澜《学习之美》

用户问五项修炼、参考答案、聚焦、模式化、四问学习法或学习迁移时，本路由负责按需检索 XP-P-049—072 和 XP-T-005 的对应选段；署名刘澜，不写成夏鹏原话。
模型定义嵌在知识卡 `model_definition` 中，不要只检索名称。引用时给 `01_source/reviewed/XP-T-005_reviewed.txt` 的实际锚点以及卡内印刷页/PDF跨页。
这次接入的24组视觉阅读记录不是全书逐字稿，也未经过独立人工校对；精确引语回查原PDF。18个公式不作为数值评分量表。
`08_ops/skill_candidates/book-learning-transfer/` 是待审阅的场景型候选，不在注册表中；不得将知识检索解释为候选技能已经启用。需要封装或修改学习流程时仍以已注册的 `scene-skill-builder` 为主，并走候选审阅流程。

# 来源

本路由可覆盖的全部登记来源：

[XP-T-001（01_source/raw/XP-T-001_raw.txt；仅文件级定位）] [XP-T-002（01_source/raw/XP-T-002_raw.txt；仅文件级定位）] [XP-T-003（01_source/raw/XP-T-003_raw.txt；仅文件级定位）] [XP-T-004（01_source/reviewed/XP-T-004_reviewed.txt）] [XP-T-005（01_source/reviewed/XP-T-005_reviewed.txt）] [XP-T-007（01_source/reviewed/XP-T-007_reviewed.txt；转写誊录+保守纠错，锚点未做独立语义复核）]
