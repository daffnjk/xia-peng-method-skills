# 在 Codex 中使用夏鹏智能体资产包

这是 Codex 原生适配版。核心映射：

- `AGENTS.md`：Codex 自动读取的项目级总规则
- `.agents/skills/*/SKILL.md`：Codex 自动发现的仓库级 Skills
- `02_knowledge/`：原则、案例、模型、冲突、主张审计
- `01_source/raw/`：课程逐字稿原始证据
- `05_user_private/`：你的个人资料（本地私有，默认 Git 忽略）
- `06_evals/`：回归测试
- `08_ops/`：新课程增量接入 SOP

## A. ChatGPT Desktop / Codex

1. 解压整个目录，不要只上传 zip。
2. 打开 ChatGPT Desktop，选择 Codex。
3. Open Folder / 打开文件夹，选择本项目根目录。
4. 第一个问题建议输入：
   `先阅读 AGENTS.md，检查可用 Skills 和现有证据范围，然后告诉我这个夏鹏智能体项目当前能做什么、不能做什么。不要修改文件。`
5. 之后可直接说任务，也可以显式指定 Skill。

## B. Codex CLI

安装（macOS/Linux）：

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

进入项目并启动：

```bash
cd /path/to/xia-peng-agent-codex-v0.1.2
codex
```

进入后：

```text
/status
/skills
```

显式调用 Skill 示例：

```text
$goal-management
领导让我下周做到 50 万营收。先区分事实、假设和缺失信息，再按目标管理流程给方案。
```

```text
$scene-skill-builder
把“客户需求访谈”做成一个可测试的 Skill，最终直接写入 .agents/skills/customer-interview/SKILL.md，并补测试题。
```

```text
$understand-me
读取 05_user_private/ 中我授权的简历和周报，生成结构化画像草案。推断不要写成事实，不要自动持久化我未确认的结论。
```

```text
$agent-team-workflow
把“为公司设计 AI 培训产品”拆成 Collector、Planner、Doer，明确交付物、验收、回退、人工审批点。
```

```text
$side-business-system
评估“中小企业 AI 工作流咨询与培训”这个方向。不要承诺收益，输出核心假设、最小验证、预算、成功阈值和停止条件。
```

```text
$career-planning
我正在考虑转岗、跳槽或发展第二曲线。先区分优势证据、个人假设与待核验的市场事实，再设计低成本、可逆的试炼方案。
```

## C. 推荐的日常使用方式

### 1. 查课程原意

```text
根据现有课程证据回答：夏鹏在 XP-T-002 中如何搭场景型 Skill？
只输出材料明确表达和材料归纳；每个关键结论给来源 ID 和文件路径。材料没讲的不要补。
```

### 2. 用夏鹏方法解决一个真实任务

```text
先调用 xia-peng-method-router 判断应该使用哪个 Skill，再执行。
我的任务是：……
已知事实：……
我的假设：……
限制条件：……
```

### 3. 让 Codex 直接维护这个项目

```text
读取 08_ops/INCREMENTAL_INGESTION_SOP.md。
把本次新课程稿件作为下一条 XP-T source 增量接入。
保留原稿，禁止静默覆盖旧原则；最后更新变更日志和相关 evals。
```

这类任务是 Codex 相比普通聊天模式更适合本项目的地方：它可以直接读写整个项目目录、修改 YAML/Markdown/JSONL、运行脚本和查看 diff。

## D. 个人资料怎么放

把简历、周报、项目复盘等放在：

```text
05_user_private/
```

根目录 `.gitignore` 默认忽略此目录中的私人内容，避免你未来把仓库推到 GitHub 时误提交。

建议文件名：

```text
05_user_private/profile.md
05_user_private/resume.pdf
05_user_private/weekly/2026-W34.md
05_user_private/projects/project-a-review.md
```

## E. 新课程怎么接入

1. 把稿件复制到 `01_source/inbox/`。
2. 在 Codex 中输入：

```text
按 08_ops/INCREMENTAL_INGESTION_SOP.md 接入 01_source/inbox/ 中的新课程。
先给我差异分析和拟修改文件清单；随后完成保守校对、知识合并、必要 Skill 更新和 eval 新增。
```

3. 完成后用 `/review` 查看变更。
4. 确认后再提交 Git。

## F. Skill 更新同步

Codex 实际读取 `.agents/skills/`。`04_skills/` 保留为旧版资产结构的兼容目录。
如果你仍然编辑 `04_skills/`，运行：

```bash
python scripts/sync_codex_skills.py
```

把修改同步到 Codex 原生目录。

## G. 最建议的第一轮测试

依次执行：

1. `/skills` —— 确认至少七个夏鹏方法论 Skill 可见（项目还可能包含其他 Skill）。
2. “解释当前项目能做什么，不修改文件。” —— 测试 AGENTS.md。
3. `$goal-management` + 一个真实任务 —— 测试场景 Skill。
4. “指出回答中哪些是材料明确表达、哪些是工程化外推。” —— 测试证据边界。
5. “完整列出夏鹏的十个教练模型。” —— 正确行为应是拒绝编造，并说明材料缺失。
6. `/review` —— 检查任何由 Codex 做出的项目文件改动。
