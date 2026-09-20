# xia-peng-method-skills

把夏鹏课程中的方法、原则、案例与边界整理成一套**可追溯、可注册、可评测、可持续扩展的 Agent Skills 方法论资产库**。

项目不是“模仿夏鹏人格”的聊天机器人，也不是独立模型服务。它更像一个带证据链的能力层：课程原稿 → 校对/定位 → 知识卡 → Skill → Router → 评测与发布门禁。适用于 Codex 等支持项目文件与 Skills 的宿主。

> **当前状态（2026-09-20）**：7 门夏鹏课程 XP-T-001/002/003/004/006/007/008 均已纳入运行时能力覆盖；其中职场沟通、极简管理、情绪管理分别由 `workplace-communication`、`minimalist-management`、`emotion-management` 独立 Skill 提供。XP-T-005 是刘澜《学习之美》外部书籍选段，不属于夏鹏课程；可通过 Router 检索知识，但独立 `book-learning-transfer` 仍保持候选状态，未绕过授权与评测门禁。

## 你可以用它做什么

| Skill | 主要用途 | 主要来源 |
| --- | --- | --- |
| `xia-peng-method-router` | 统一识别任务、选择一个主 Skill、控制证据与授权边界 | XP-T-001—008 |
| `understand-me` | 在授权资料范围内整理画像差异与待确认事实 | XP-T-001 |
| `scene-skill-builder` | 把工作方法封装为可评测候选 Skill | XP-T-002 |
| `goal-management` | 目标口径、路径、资源、节奏、汇报与复盘 | XP-T-002 |
| `agent-team-workflow` | Collector / Planner / Doer 等角色与契约设计 | XP-T-003 |
| `side-business-system` | 主业约束下的可逆副业验证 | XP-T-003/004 |
| `career-planning` | 优势证据、岗位/行业/公司/城市/学历与第二曲线决策 | XP-T-001/004 |
| `workplace-communication` | 向上、向下、平级与客户沟通；减少误解、建立信任、推动结果 | XP-T-006 |
| `minimalist-management` | KPI/OKR、会议、情景领导、授权激励、绩效面谈、新接团队 | XP-T-007 |
| `emotion-management` | 当下情绪、近期反应、长期重复内耗、事实/信念/选择拆分 | XP-T-008 |

声明版本、依赖与来源以 [Skill 注册表](03_agent/skill_registry.json) 为准。`create-readme` 是开发辅助 Skill，不进入运行包。

## 快速开始

完整克隆仓库，在根目录执行（Python 3.11+）：

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

python -m pip install -r requirements-dev.txt
python scripts/assets.py validate
python -m unittest discover -s tests -v
python scripts/assets.py build
python scripts/assets.py validate --check-build
```

构建产物在 `dist/`：

- `dist/runtime/`：内部运行目录；
- `dist/runtime.zip`：确定性运行包；
- `dist/review_dashboard.html`：知识审阅页；
- `dist/eval-prompts.jsonl`：隔离后的评测输入；
- `dist/golden_questions.md`：评测人员视图，**不得提供给被测模型**。

运行包不会包含 `05_user_private/`、`01_source/inbox/`、题库预期、测试文件或开发辅助 Skill。

## 在 Codex 中使用

打开仓库后，首次建议输入：

```text
阅读 AGENTS.md、03_agent/METHOD_POLICY.md 和 03_agent/skill_registry.json。
说明当前来源边界、可用 Skill 与引用限制，不修改文件。
```

之后直接描述任务，Router 会选择主能力；也可以显式调用：

```text
$workplace-communication
我明天要和领导谈资源不足，帮我把目标、事实、诉求、交换条件和时间节点整理清楚。
```

```text
$emotion-management
我连续几年遇到类似场景都会爆发，帮我先判断这是一次事件还是长期重复模式，再选一个模型处理。
```

```text
$minimalist-management
我下周接手一个成熟团队，帮我按课程框架设计第一个月的管理顺序。
```

详细说明见 [Codex 使用指南](README_CODEX.md)。单独复制某个 `SKILL.md` 不等于带走其公共规则、知识与来源证据。

## 来源覆盖与注册规则

### 夏鹏课程

| Source ID | 内容 | 运行时覆盖 |
| --- | --- | --- |
| XP-T-001 | 让智能体懂你 | `understand-me` / `career-planning` |
| XP-T-002 | 场景型 Skill 与目标管理 | `scene-skill-builder` / `goal-management` |
| XP-T-003 | 多 Agent 工作流与变现系统 | `agent-team-workflow` / `side-business-system` |
| XP-T-004 | 职业规划 | `career-planning` |
| XP-T-006 | 职场沟通实讲 | `workplace-communication` |
| XP-T-007 | 极简管理课 | `minimalist-management` |
| XP-T-008 | 情绪管理 | `emotion-management` |

校验器要求所有 `knowledge_extracted` 来源必须被主 Router 覆盖；以后新增课程如果完成知识提取却忘记注册，CI 会直接失败。

### 外部书籍 XP-T-005

XP-T-005 是刘澜《学习之美》的 24 组选段视觉阅读记录，不是夏鹏课程，也不是全书逐字稿。新增知识卡 XP-P-049—072 保留原作者归属。18 个学习力公式按关系隐喻处理，不作为数值诊断或成功率预测。

`08_ops/skill_candidates/book-learning-transfer/` 仍是候选能力，未进入 `.agents/skills/`；对外授权仍待确认，因此不能因为“课程全部上线”而顺带把该外部书籍候选公开启用。

## 架构

```text
01_source/          原稿、校对稿、manifest、来源哈希锁
02_knowledge/       原则 / 案例 / 模型 / 冲突 / 风险主张知识卡
03_agent/           公共运行规则与 Skill 注册表
.agents/skills/     唯一 Skill 编辑源与自动发现入口
04_skills/          兼容占位；禁止反向同步
05_user_private/    本地授权个人资料；不进入分发包
06_evals/           JSONL 行为题库；不进入被测模型上下文
07_deployment/      部署与上传说明
08_ops/             接入 SOP、迁移、审阅与发布流程
schemas/            数据契约
scripts/            校验、构建、来源解析、接入与评分工具
tests/              工程回归与资产契约测试
dist/               自动生成；不编辑、不提交
```

唯一维护源原则：

- Skill 只编辑 `.agents/skills/`；
- 知识只编辑 `02_knowledge/*.yaml`；
- 公共方法规则只编辑 `03_agent/METHOD_POLICY.md`；
- 题库只编辑 `06_evals/*.jsonl`；
- `dist/` 只能由构建生成。

## 证据与引用

```bash
python scripts/assets.py resolve XP-T-006#P003-P013
python scripts/assets.py resolve XP-T-008#P034-P037
python scripts/assets.py resolve XP-T-001
```

`resolve` 只证明来源文件和锚点存在，不证明该片段一定支持某个结论。

XP-T-001—003 当前仍只有文件级定位；不得生成未经核对的旧 `#Pxxx`。XP-T-004、006、007、008 可使用 reviewed 文件中的真实段落锚点，但回答仍需检查语义。外部理论、市场数据、公司政策、薪酬、法律和医疗事实需要单独核验，不能因为课程提到就自动视为当前事实。

## 新课程接入

先登记，不自动上线：

```bash
python scripts/scaffold_new_course.py --title "新课程" --transcript /path/to/transcript.txt
```

标准流程：

```text
received
  ↓
校对/来源锁
  ↓
知识提取
  ↓
候选 Skill
  ↓
人工审阅 + 评测覆盖
  ↓
注册表 + Router
  ↓
内部运行包
  ↓
满足授权/证据/行为报告后才允许公共发布
```

详见 [增量接入 SOP](08_ops/INCREMENTAL_INGESTION_SOP.md)。

## 验证与发布边界

工程校验：

```bash
python scripts/assets.py validate
python -m unittest discover -s tests -v
python scripts/assets.py build
python scripts/assets.py validate --check-build
```

真实行为验收必须在实际宿主/模型上执行。CI 通过只表示数据契约、引用、构建与工程测试通过，**不表示课程结论真实、模型行为合格或公共分发授权完整**。

公共发布默认被阻止；只有精确证据、来源授权、命名审批和与同一资产版本绑定的行为评分报告同时满足要求时，`build --public` 才能通过。不要通过修改授权或评分来“让发布成功”。

## 维护文档

- [项目工程规则](AGENTS.md)
- [公共方法规则](03_agent/METHOD_POLICY.md)
- [架构说明](08_ops/ARCHITECTURE.md)
- [接入 SOP](08_ops/INCREMENTAL_INGESTION_SOP.md)
- [评测说明](06_evals/README.md)
- [贡献指南](CONTRIBUTING.md)
- [变更记录](CHANGELOG.md)
