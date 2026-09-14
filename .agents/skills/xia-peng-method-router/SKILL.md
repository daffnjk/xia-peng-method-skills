---
name: xia-peng-method-router
description: 路由夏鹏智能体方法论与职业规划任务；覆盖个性化、场景型 Skill、目标管理、多 Agent、副业验证和职业/生涯选择；另含刘澜《学习之美》的学习方法与迁移参考。
version: 0.4.0
---

先读取并遵守 `03_agent/METHOD_POLICY.md`，包括直接显式调用本 Skill 的情况。依赖与可选辅助能力见 `03_agent/skill_registry.json`。这是方法流程，不代表已执行任何工具动作。

复合任务只选一个主 Skill，按 `03_agent/skill_registry.json` 补必要辅助能力；复用已授权上下文，禁止无界递归和重复画像收集。

# 目标

判断用户请求属于哪个方法模块；夏鹏观点限于已接入课程，刘澜《学习之美》作为单独署名的外部参考。

# 路由

1. 个人资料与“懂我” → `understand-me`
2. 把工作方法做成 Skill → `scene-skill-builder`
3. 目标拆解、资源、汇报、复盘 → `goal-management`
4. 多 Agent 角色与闭环 → `agent-team-workflow`
5. 副业候选、评估、执行 → `side-business-system`
6. 优势识别、岗位匹配、跳槽/转行、offer/行业/公司/城市/学历决策、第二曲线 → `career-planning`
7. 《学习之美》、刘澜学习方法、读懂却不会用、学习迁移或知识碎片化 → 由本 Router 按需读取 [应用方法](references/liulan-learning-practice.md)；问全书内容、案例或具体模型时查 [全书提炼](references/liulan-learning-book.md)，来源信息见 [来源记录](references/liulan-learning-source.json)。不默认加载整本提炼。
8. 询问夏鹏材料原意 → 检索原始/校对逐字稿和知识卡
9. 其他夏鹏观点 → 明确“材料不足”，不得外推成完整人格

# 来源规则

- 明确表达、材料归纳、工程化外推必须分开。
- 任何“夏鹏认为”按公共规则给来源 ID 与真实文件路径；不得补造锚点。
- 不使用讲者的贬损、竞品攻击、价格与课程销售话术。
- XP-T-004 中的公司、行业、城市、薪资、学历和平台例子是录制时材料；当前决策需重新核验。
- 人格/兴趣测评、年限、能力百分位和收入公式只能作启发，不得作确定性诊断或承诺。
