---
name: understand-me
description: 基于获授权的个人资料建立和维护结构化用户画像，用于后续个性化建议与执行。
version: 0.3.0
---

先读取并遵守 `03_agent/METHOD_POLICY.md`，包括直接显式调用本 Skill 的情况。依赖与可选辅助能力见 `03_agent/skill_registry.json`。这是方法流程，不代表已执行任何工具动作。

# 适用场景

用户上传简历、自我介绍、工作日志、测评、项目材料，或要求智能体更懂自己。

# 输入

- 简历与职业经历
- 自我介绍
- 工作周报/年终总结
- 公开或用户主动提供的测评结果
- 项目成果与复盘
- 用户明确允许保存的对话事实

# 工作流

1. 建立资料清单：来源、日期、权限、主体、有效期。
2. 提取五类信息：
   - 可核验事实
   - 用户自述
   - 测评结果
   - 模型推断
   - 待确认/冲突信息
3. 生成画像：经历、优势证据、偏好、目标、约束、组织环境、当前项目。
4. 对每条推断给出证据与置信度。
5. 让用户审核后再写入长期画像。
6. 每周生成增量报告；每季度生成简历变更候选。
7. 后续建议必须说明调用了哪些画像信息；用户可关闭个性化。

# 输出

- `05_user_private/drafts/user_profile.md`
- `05_user_private/drafts/profile_facts.jsonl`
- `05_user_private/drafts/open_questions.md`
- `05_user_private/drafts/weekly_delta.md`

# 禁止事项

- 不默认聊天历史就是长期记忆。
- 不把 MBTI/盖洛普当作确定性人格诊断。
- 不把计划或自我评价写成已完成成果。
- 不收集与任务无关的敏感信息。

# 来源

[XP-T-001（01_source/raw/XP-T-001_raw.txt；仅文件级定位）] [XP-T-001（01_source/raw/XP-T-001_raw.txt；仅文件级定位）] [XP-T-001（01_source/raw/XP-T-001_raw.txt；仅文件级定位）]
