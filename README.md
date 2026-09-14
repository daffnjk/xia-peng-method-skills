# xia-peng-method-skills

基于有限课程材料整理的**非官方、证据驱动型方法论资产库**。主要供 Codex 等宿主使用，覆盖个人画像、场景 Skill、目标管理、多 Agent 工作流设计、副业验证和职业规划；不冒充夏鹏本人，不自带模型后端、长期记忆服务或多 Agent 调度器。

> 当前四个来源中，XP-T-001—003 只能提供文件级定位；XP-T-004 有可解析的校对稿段落。构建和静态测试不能证明课程结论正确或模型行为通过。对外分发授权与严格行为验收仍需单独确认。

## 快速开始

完整克隆本仓库，在仓库根目录执行（Python 3.11+）：

```bash
python -m venv .venv
# macOS / Linux：source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts/assets.py validate
python -m unittest discover -s tests -v
python scripts/assets.py build
python scripts/assets.py validate --check-build
```

构建产物在 `dist/`：`runtime/` 与 `runtime.zip` 是内部运行包；`review_dashboard.html` 是自动生成的知识审阅页；`golden_questions.md` 是评测人员视图，**不要提供给被测模型**。运行包不包含私人目录、inbox、题库预期或第三方开发辅助 Skill。

在 Codex 中打开仓库，先输入：

```text
阅读 AGENTS.md 和 03_agent/METHOD_POLICY.md，说明当前证据范围与可用 Skill，不修改文件。
```

然后直接描述任务，或显式调用 `$career-planning`、`$goal-management` 等。详细说明见 [Codex 使用指南](README_CODEX.md)。单独复制某个 `SKILL.md` 不等于带走其证据和公共规则。

## 能力与依赖

| Skill | 作用 |
| --- | --- |
| `xia-peng-method-router` | 一个主流程，按需加入辅助能力，控制材料边界 |
| `understand-me` | 读取授权资料，生成待确认画像差异 |
| `scene-skill-builder` | 生成可评测的候选 Skill，审核后再启用 |
| `goal-management` | 目标口径、路径、资源、节奏、汇报与复盘 |
| `agent-team-workflow` | 设计 Collector / Planner / Doer 的责任、契约和回退 |
| `side-business-system` | 在现实约束下设计可逆副业验证 |
| `career-planning` | 优势证据、职业选项、试炼与回退路径 |

声明版本与可选依赖以 [Skill 注册表](03_agent/skill_registry.json) 为准。`create-readme` 是原有第三方开发辅助工具，不属于方法论运行包。

## 架构与唯一维护源

```text
01_source/          原稿、校对稿、登记清单与来源哈希锁
02_knowledge/       YAML 知识卡：原则、案例、模型、冲突、风险主张
03_agent/           公共运行规则与 Skill 注册表
.agents/skills/     唯一 Skill 编辑源
05_user_private/   本地授权资料；不进入分发包
06_evals/          JSONL 题库与评分规则；不进入被测模型上下文
08_ops/            接入、审阅、迁移记录和发布流程
schemas/           版本化数据契约
scripts/           校验、构建、检索上下文、接入与评测工具
tests/            合成资料单元测试
dist/             自动生成，不编辑、不提交
```

`04_skills/` 已退出编辑流程，不再反向同步。原则 JSONL、黄金题展示、审阅页面由源资产生成，不保留第二个独立编辑源。公共方法规则只有 [METHOD_POLICY.md](03_agent/METHOD_POLICY.md) 一份；平台系统提示词由构建复制，工程维护规则留在 [AGENTS.md](AGENTS.md)。

## 证据与引用命令

```bash
python scripts/assets.py resolve XP-T-004#P012-P020
python scripts/assets.py resolve XP-T-001
```

`resolve` 只验证文件和锚点，不验证语义支持。前三个来源的旧 `#Pxxx` 已归档到 `legacy_source_refs`，不能继续作为有效引用。知识关联由宿主按注册表和来源字段完成，本仓库不提供语义检索器。

## 维护与评测

新课程先暂存：

```bash
python scripts/scaffold_new_course.py --title "新课程" --transcript /path/to/transcript.txt
```

脚本只登记，不自动校对、提取、授权或发布。已登记 ID 或相同稿件拒绝重复创建；失败后按提示处理，不删除仍可能被使用的锁。见 [接入 SOP](08_ops/INCREMENTAL_INGESTION_SOP.md)。

真实行为评测需要选定宿主和模型。可先生成隔离输入，再由外部宿主逐题执行；评分记录绑定资产和题库摘要，缺题、低分、失效引用或严重越界均不通过。见 [评测说明](06_evals/README.md)。

```bash
python scripts/assets.py prepare-eval
python scripts/assets.py grade-eval /path/to/scored-report.json
```

公共发布默认被阻止；只有精确证据、授权状态、命名审批和同版本行为报告都满足要求时，`build --public --approval ... --report ...` 才能成功。不要为了让发布通过，修改授权或评分为未经确认的值。

架构决策与迁移边界见 [架构说明](08_ops/ARCHITECTURE.md)，贡献流程见 [CONTRIBUTING.md](CONTRIBUTING.md)，变更见 [CHANGELOG.md](CHANGELOG.md)。
