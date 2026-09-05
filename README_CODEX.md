# 在 Codex 中使用本项目

[返回项目首页](README.md) · [贡献指南](CONTRIBUTING.md) · [评测说明](06_evals/README.md)

## 1. 准备环境

使用完整仓库，不要只复制 `SKILL.md`：技能会引用项目中的知识卡、原稿和治理文件。需要已安装并完成登录的 Codex；维护脚本建议使用 Python 3.10+，无需安装第三方 Python 包。

Codex 的安装、登录、界面和权限选项以 [官方 CLI 指南](https://developers.openai.com/codex/cli/) 为准。macOS/Linux 的官方独立安装命令为：

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

该命令会下载并执行安装脚本，请先确认来源并遵守所在组织的软件安装要求。其他系统或安装方式使用官方指南中的对应选项。本项目不固定 Codex 版本；记录实际使用的版本便于复现。

```bash
cd /path/to/xia-peng-method-skills
python3 scripts/verify_codex_setup.py
python3 scripts/sync_codex_skills.py --check
codex --version
codex
```

桌面客户端或 IDE 中，请打开同一个项目根目录，并使用可访问这些本地文件的 Codex 工作区；具体入口以当前客户端为准。仅在普通对话中上传一个压缩包，不等于配置了本地项目与技能发现。

## 2. 文件如何生效

| 入口 | 用途 |
| --- | --- |
| `AGENTS.md` | 项目总规则、证据范围、资料隐私与工作边界 |
| `.agents/skills/*/SKILL.md` | Codex 发现和调用的项目技能 |
| `02_knowledge/` | 原则与案例检索，以及模型、冲突、风险主张核查 |
| `01_source/` | 根据 manifest 回查原稿和实际存在的校对稿 |
| `05_user_private/` | 经用户授权的本地画像上下文，不是课程证据 |
| `06_evals/` | 行为回归题目与评分标准，不会自动运行 |

规则读取和技能发现分别参见 [官方 AGENTS.md 文档](https://developers.openai.com/codex/guides/agents-md/) 与 [官方 Skills 文档](https://developers.openai.com/codex/skills/)（外部说明核对日期：2026-09-05）。全局或子目录规则可能影响实际行为，应先核对加载结果。

## 3. 第一次只读验收

```text
先阅读 AGENTS.md，检查可用 Skills 和 01_source/manifest.csv。
说明项目当前能做什么、不能做什么；列出来源文件和待确认事项。
不要修改文件，不读取未经我授权的个人资料。
```

在 Codex CLI 中使用 `/skills` 或输入 `$` 选择技能。预期包含七个方法论 Skill，另有 `create-readme` 等维护辅助技能。命令输入在 Codex 会话中，不是在系统 shell 中执行。

## 4. 常用任务示例

### 查询材料原意

```text
根据现有课程证据回答：XP-T-002 中如何搭场景型 Skill？
区分材料明确表达与材料归纳；每个关键结论给来源 ID 和文件路径。
遇到无法定位的历史段落号时回查原稿，不要伪造锚点。
```

### 目标管理

```text
$goal-management
领导要求下周完成一个新客户试点。先区分事实、假设和缺失信息，
再给出目标、资源、节奏、验收、汇报与复盘方案。
```

### 个人画像

```text
$understand-me
仅读取我明确授权的 05_user_private/profile.md 和指定周报，生成画像草案。
区分事实、自述、测评和推断，不自动保存未经确认的结论。
```

上述文件是本地示例，不随仓库提供；先创建或替换成实际授权路径。

### 场景 Skill 与协作

```text
$scene-skill-builder
把“客户需求访谈”做成可测试的 Skill。先给输入输出、流程和验收标准，
再提出文件变更方案；共享方法论资产按贡献指南同步两处目录，并补测试题。
```

```text
$agent-team-workflow
把“设计企业 AI 培训产品”拆成 Collector、Planner、Doer，
明确交付物、验收、失败回退和人工审批点；不要假定已配置自动执行引擎。
```

### 副业与职业规划

```text
$side-business-system
评估一个企业工作流咨询方向。不承诺收益，输出假设、最小验证、预算、
成功阈值和停止条件，并标明需要核验的市场信息。
```

```text
$career-planning
我在考虑转岗、跳槽或第二曲线。先核对优势证据和限制条件，
再设计低成本、可逆试炼；当前薪资、岗位和行业事实另行核验。
```

## 5. 修改、同步与评测

共享 Skill 的维护源是 `04_skills/`，Codex 运行目录是 `.agents/skills/`。不要只修改运行副本后直接强制同步；先决定哪一份变更应保留。

```bash
python3 scripts/sync_codex_skills.py --dry-run
git diff -- 04_skills .agents/skills
# 审阅并确认同步源后，才显式允许覆盖已有差异
python3 scripts/sync_codex_skills.py --force
python3 scripts/sync_codex_skills.py --check
python3 scripts/verify_codex_setup.py
python3 -m unittest discover -s tests -v
git diff --check
```

同步保留目标独有的文件与技能，不自动处理删除或重命名。详细参数与行为见 [项目首页](README.md)。改动 Skill、规则或知识时，还要执行 [行为回归](06_evals/README.md)，不能用脚本 `PASS` 替代。

新课程按 [增量接入 SOP](08_ops/INCREMENTAL_INGESTION_SOP.md) 操作；先登记授权和唯一来源 ID，再进行知识合并。使用 `/review` 或 Git diff 审阅变更，确认没有原稿覆盖、私人资料或意外文件后再提交。

## 6. 排查常见问题

| 现象 | 检查方式 |
| --- | --- |
| 找不到技能 | 确认项目根目录、隐藏的 `.agents/`、`SKILL.md` 的 `name` / `description`；必要时重启 Codex |
| 同步报已有内容不同 | 先比较并保留正确版本；只有确认源内容应胜出时才使用 `--force` |
| 设置检查通过但回答不正确 | 设置检查不验证模型行为；按题库、评分量表和来源回查定位问题 |
| 课程引用无法定位 | 使用 manifest 的真实路径；不要把历史 `#Pxxx` 标号当成已存在的锚点 |
| Git 中出现个人资料 | 检查是否已被跟踪或使用了强制添加；停止分享并按团队流程处理，不依赖 `.gitignore` 补救历史记录 |
