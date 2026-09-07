# xia-peng-method-skills

基于夏鹏老师课程材料整理的**非官方方法论知识库与 Agent Skills**：把个人画像、场景型 Skill、目标管理、多 Agent 协作、副业验证和职业规划整理成有来源、有边界、可复盘的工作流程。

这是一套以 Markdown、YAML、JSONL 和 Python 维护脚本组成的资产库，不是独立运行的聊天服务，也不包含模型、自动检索服务或自动执行的多 Agent 引擎。

> [!IMPORTANT]
> 项目不是夏鹏本人，不代表其授权或完整观点。课程的使用范围以 [来源清单](01_source/manifest.csv) 为准：`XP-T-001`—`003` 的授权状态尚未记录，`XP-T-004` 为内部使用、待确认。不要据此公开分发原稿或直接发布对外产品。

[Codex 使用指南](README_CODEX.md) · [部署指南](07_deployment/MVP_DEPLOYMENT_GUIDE.md) · [贡献指南](CONTRIBUTING.md) · [评测说明](06_evals/README.md) · [项目分析与待办](08_ops/PROJECT_REVIEW.md) · [变更记录](CHANGELOG.md)

## 能解决什么问题

| Skill | 适用任务 | 主要交付物 |
| --- | --- | --- |
| [xia-peng-method-router](.agents/skills/xia-peng-method-router/SKILL.md) | 不确定该用哪套方法 | 任务路由、证据范围与边界判断 |
| [understand-me](.agents/skills/understand-me/SKILL.md) | 整理经授权的简历、周报、项目资料 | 区分事实、自述、推断的画像草案 |
| [scene-skill-builder](.agents/skills/scene-skill-builder/SKILL.md) | 将重复工作封装成 Skill | 场景、流程、输入输出、验收与测试题 |
| [goal-management](.agents/skills/goal-management/SKILL.md) | 拆解目标并落实执行 | 上下文、资源、行动节奏、汇报与复盘 |
| [agent-team-workflow](.agents/skills/agent-team-workflow/SKILL.md) | 设计多人或多 Agent 协作 | Collector / Planner / Doer 的交接、验收与审批点 |
| [side-business-system](.agents/skills/side-business-system/SKILL.md) | 验证副业或服务方向 | 核心假设、低成本验证、预算与停止条件 |
| [career-planning](.agents/skills/career-planning/SKILL.md) | 转岗、跳槽、offer 比较与第二曲线 | 优势证据、决策比较与可逆试炼方案 |

仓库另有 [`create-readme`](.agents/skills/create-readme/SKILL.md) 文档维护辅助 Skill，不计入上述七个方法论 Skill。

## 快速开始

### 1. 获取完整仓库

需要 Git；运行维护脚本和测试时建议使用 Python 3.10 或更高版本，脚本仅使用标准库。Codex 需单独安装并完成登录，安装入口见 [Codex 使用指南](README_CODEX.md)。

```bash
git clone https://github.com/daffnjk/xia-peng-method-skills.git
cd xia-peng-method-skills
python3 scripts/verify_codex_setup.py
python3 scripts/sync_codex_skills.py --check
```

私有仓库需要具有访问权限的 GitHub 身份。下载 ZIP 时必须完整解压，并确认 `.agents/` 没有被遗漏。Windows 下可将 `python3` 替换为本机对应的 Python 命令。

### 2. 从项目根目录启动 Codex

```bash
codex
```

第一次先进行只读检查：

```text
先阅读 AGENTS.md，检查 .agents/skills/ 和现有来源清单。
说明当前项目能做什么、不能做什么，并指出材料不足之处。不要修改文件。
```

然后在 Codex CLI 中使用 `/skills` 查看技能，或显式调用：

```text
$goal-management
我要在四周内完成一个客户试点。先区分事实、假设和缺失信息，
再给出资源需求、阶段交付物、验收指标、风险与停止条件。
```

```text
$career-planning
我在比较转岗和留任。先列出需要核实的优势证据与市场信息，
再设计低成本、可逆的试炼；不要凭人格测评或历史案例直接替我定职业。
```

Codex 的项目规则与技能发现机制见 [官方 AGENTS.md 文档](https://developers.openai.com/codex/guides/agents-md/) 和 [官方 Skills 文档](https://developers.openai.com/codex/skills/)。其他平台需按 [部署指南](07_deployment/MVP_DEPLOYMENT_GUIDE.md) 显式配置，不能假定自动读取这些目录。

## 当前证据范围

| 来源 ID | 内容 | 仓库中的证据文件 |
| --- | --- | --- |
| XP-T-001 | 让智能体懂你 | [原稿](01_source/raw/XP-T-001_raw.txt) |
| XP-T-002 | 场景型 Skill 与目标管理 | [原稿](01_source/raw/XP-T-002_raw.txt) |
| XP-T-003 | 多 Agent 工作流与变现系统 | [原稿](01_source/raw/XP-T-003_raw.txt) |
| XP-T-004 | 职业规划，12 讲 | [原稿](01_source/raw/XP-T-004_raw.txt) · [带稳定锚点的校对稿](01_source/reviewed/XP-T-004_reviewed.txt) |

回答应区分 **材料明确表达 / 材料归纳 / 工程化外推 / 材料不足**。关键结论应给出来源 ID 和实际文件路径，必要时回查原稿。`XP-T-001`—`003` 的历史 `#Pxxx` 引用尚需补齐映射，不能当成已验证的文件锚点；详情见 [评测说明](06_evals/README.md)。

“十个教练模型”和完整职业教练 Skill 等材料仍缺失；不得补造。当前岗位、薪资、行业、平台能力与收益类信息需要重新核验，课程例子不等于当前事实或结果保证。

## 仓库结构

```text
.agents/skills/       Codex 实际读取的技能目录
01_source/           来源清单、原稿、校对稿、收件箱与纠错记录
02_knowledge/        原则、案例、模型、冲突、风险主张与思维导航
03_agent/            通用 SYSTEM_PROMPT.md
04_skills/           七个方法论 Skill 的兼容资产与同步源
05_user_private/     本地个人资料；除说明文件外默认 Git 忽略
06_evals/            黄金题、JSONL 题库、评分量表与执行说明
07_deployment/       平台部署、资料上传与审阅说明
08_ops/              课程接入、合并决策、发布清单与项目分析
scripts/             环境检查、Skill 同步、新课程登记
tests/              维护脚本的单元测试
AGENTS.md            项目级行为规则与证据边界
review_dashboard.html  审阅页面
```

## 维护与检查

七个共享方法论 Skill 的维护约定是：**修改 `04_skills/`，审阅后同步到 `.agents/skills/`，两处一起提交**。仅在运行目录中存在的辅助 Skill 单独维护。新克隆的仓库不需要先强制同步。

```bash
# 只读检查；缺失或不同返回非零退出码
python3 scripts/sync_codex_skills.py --check

# 预览，不写入文件
python3 scripts/sync_codex_skills.py --dry-run

# 默认只补缺失文件；发现已有文件不同则整轮停止写入
python3 scripts/sync_codex_skills.py

# 仅在确认兼容源内容应覆盖同名目标文件后使用
python3 scripts/sync_codex_skills.py --force

# 维护脚本测试，不调用模型
python3 -m unittest discover -s tests -v
```

同步不会删除目标目录独有的文件或 Skill；重命名、删除和双向合并仍需人工审阅。`--check` 仅比较同步源包含的文件，不是完整目录镜像检查。

`verify_codex_setup.py` 的 `PASS` 只代表基本文件与 Skill 元信息检查通过；单元测试通过也不代表模型回答正确。行为回归需要按 [评测说明](06_evals/README.md) 另行执行并记录结果。

新增课程从 [增量接入 SOP](08_ops/INCREMENTAL_INGESTION_SOP.md) 开始，发布前检查 [发布清单](08_ops/RELEASE_CHECKLIST.md)。个人资料只放入明确授权的本地位置；`.gitignore` 不是访问控制，也不会移除已经提交的资料。
