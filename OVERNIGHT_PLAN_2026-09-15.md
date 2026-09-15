# 整夜优化任务计划（2026-09-15）

本文件是给一个在 `E:\zcode\xiapeng` 工作区内运行的智能体的完整执行指令。目标：在一个晚内完成 xiapeng skills 资产库的低风险优化，全程可回滚、可断点续跑、不留未报告的验证缺口。

执行前先通读本文件和 `AGENTS.md`。方法论规则以 `03_agent/METHOD_POLICY.md` 为准。

## 0. 环境事实（2026-09-15 已核实，直接使用，不要重新探测）

- 本工作区**没有 `.git`，也没有安装 git.exe**。版本安全靠阶段快照（见 P0）。不要尝试安装 Git、不要用 gh 操作远端。
- `gh.exe` 在 `C:\Program Files\GitHub CLI\gh.exe`（已登录 daffnjk），但本计划**不需要也不允许**任何远端操作。
- 默认 `python` 是 3.6.6，跑不了 jsonschema 4.26。**所有 Python 命令一律用 `py -3`（3.12.10）**。
- 仓库基线：8 个单文件 Skill（7 个项目 Skill + dev-only 的 create-readme），注册表 `03_agent/skill_registry.json`，2026-09-15 审计结论为"架构良好，不重构"。

## 红线（任何阶段都不得违反）

1. 不编辑 `dist/`、`01_source/`、`04_skills/`；不删除任何原始证据。
2. 不为 XP-T-001—003 创建或复用 `#Pxxx` 段落引用；历史编号只存在于 `legacy_source_refs`。
3. 不把 `08_ops/skill_candidates/` 里的候选 Skill（如 book-learning-transfer）移入 `.agents/skills/` 或注册。
4. 不改知识卡 `02_knowledge/*.yaml` 和题库 `06_evals/*.jsonl` 的内容。
5. 不做真实宿主回归（夜间无适配器和宿主）——因此**不合并、不发布、不宣称行为验收通过**；SKILL.md 的改动在报告中明确标注"真实宿主回归未执行，待用户安排"。
6. 遇到无法用本计划内的步骤解释的异常：恢复最近快照，停止执行，写报告。不要即兴扩大范围。

## 进度日志与断点续跑

每完成一个编号步骤，就在 `E:\zcode\xiapeng\_overnight_progress.md` 追加一行：

```
[YYYY-MM-DD HH:MM] 步骤编号 | 结果(ok/fail) | 一句话备注
```

会话中断后重启的智能体：先读本计划和 `_overnight_progress.md`，从最后一个 ok 步骤的下一步继续，不重做已完成步骤。

## P0 环境与基线（约 30 分钟）

1. 建快照目录并做基线快照（后续每个 Phase 结束再各做一次，命名 `phase<N>-<HHMM>.zip`）：
   ```cmd
   if not exist E:\zcode\xiapeng-snapshots mkdir E:\zcode\xiapeng-snapshots
   powershell -NoProfile -Command "Compress-Archive -Path 'E:\zcode\xiapeng\*' -DestinationPath 'E:\zcode\xiapeng-snapshots\phase0-baseline.zip' -Force"
   ```
2. 安装依赖并跑完整基线（记录每条命令的退出码和输出摘要到进度日志）：
   ```cmd
   cd /d E:\zcode\xiapeng
   py -3 -m pip install -r requirements-dev.txt
   py -3 scripts\assets.py validate
   py -3 -m unittest discover -s tests -v
   py -3 scripts\assets.py build
   py -3 scripts\assets.py validate --check-build
   py -3 scripts\assets.py validate --strict-evidence
   ```
   - `--strict-evidence` 只记录结果，不作为门禁（文档化的门禁是普通 validate）。
   - **门禁**：validate / unittest / build / check-build 四项全绿才继续。任何一项红：不要修复，写明现象，终止计划并报告（基线就红说明仓库先于本计划有问题，需要用户决策）。

## P1 三个已审计确认的修复（约 1.5 小时）

这三项来自 2026-09-15 审计，用户发起本计划即视为批准执行。每项完成后单独跑 `validate + unittest`，绿了才做下一项；红了恢复 phase0 快照中该文件并记录。

### 修复 A：五个 Skill 的重复引用脚注去重
- 对象：`understand-me`、`goal-management`、`agent-team-workflow`、`scene-skill-builder`、`side-business-system` 的 SKILL.md。
- 先用文本搜索确认每个文件里 `# 来源` 家族标题（来源/来源规则/来源边界）确实出现多个语义重复的块；把重复块合并为**一个**脚注节，保留全部 `XP-T-###(#P…)` 引用的并集。
- 硬约束：合并前后文件正则口径的来源 ID 集合不变（validator 用 `XP-T-\d{3,}(?:#P…)?` 扫全文并与注册表比对）——只删重复文本，不删任何唯一 ID。
- 来源：重复是 `scripts/migrate_architecture.py:163` 把逐段引用坍缩成文件级引用时遗留的。

### 修复 B：脚注与注册表对齐
- `side-business-system`：注册表声明 XP-T-003+XP-T-004，脚注只写了 XP-T-003 → 脚补上 XP-T-004。
- `career-planning`：注册表声明 XP-T-001+XP-T-004，脚注只覆盖 XP-T-004 → 脚补上 XP-T-001。
- 只改脚注文本（正文中已有这些 ID，全文集合不变）；XP-T-001—003 是文件级引用，脚注里不得带 `#Pxxx`。

### 修复 C：understand-me 的周期性承诺改口径
- 工作流第 6 步承诺"每周/每季度报告"与 `08_ops/ARCHITECTURE.md`、`03_agent/METHOD_POLICY.md` 的"无调度器、无长期任务"矛盾。
- 改为按调用口径：每次被调用时输出自上次调用以来的画像增量与待确认项；不做任何周期性/后台任务承诺。改动最小化，只动这一处措辞。

### 版本与变更记录
- 本 Phase 每个被编辑的 SKILL.md：frontmatter `version` 0.3.1→0.3.2，**同步改 `03_agent/skill_registry.json` 里同名条目的 version**（validator 要求两者相等）。xia-peng-method-router（0.3.2）若未编辑则不动。
- 在根目录 `CHANGELOG.md` 追加一条 2026-09-15 记录，说明 A/B/C 三项。
- Phase 结束：validate + unittest + 快照 `phase1-<HHMM>.zip`。

## P2 新增防回归检查（约 1.5 小时）

把审计发现变成永久门禁，这是本次夜间最有长期价值的部分。改 `scripts/assets.py`（必要时 `scripts/assetlib.py`），先写测试再实现：

1. **脚注一致性检查**：每个 `.agents/skills/` 项目 Skill 的脚注节（最后一个 `# 来源*` 标题之后的文本）中的来源 ID 集合 == 注册表 `source_refs`。create-readme（dev skill）豁免。
2. **重复脚注检查**：同一 SKILL.md 中出现多个语义重复的 `# 来源` 家族标题（如同名标题重复出现）即报错。
3. 测试：在 `tests/test_assets.py`（或新建 `tests/test_footer_checks.py`）用 `tests/fixtures/` 合成数据各加一个正例一个反例，遵循现有测试风格（合成、非个人数据）。
4. 门禁：新测试通过 + 旧测试不回归 + validate 全绿。快照 `phase2-<HHMM>.zip`。

实现约束：检查逻辑放在现有 Catalog/validate 流程里，报错风格与现有错误一致，不引入新依赖、不加配置项。

## P3 全库一致性巡检（约 1.5 小时，只读为主）

逐项检查并记录，**只应用零风险修复**（错别字、失效路径修正）；凡涉及行为规则、方法论语义的发现一律只写进报告"建议、未改"：

1. 7 个项目 Skill 的引导语（"先读取并遵守 `03_agent/METHOD_POLICY.md`…"）措辞一致性。
2. 每个 SKILL.md 中引用的仓库内相对路径真实存在（死链清单）。
3. `xia-peng-method-router` 的路由描述覆盖全部 7 个项目 Skill，无遗漏无多余。
4. 注册表 `resources: []` 与各 Skill 目录实际内容一致；`development_skills` 仅 create-readme；候选目录隔离未被破坏。
5. `03_agent/METHOD_POLICY.md` 与各 SKILL.md 无规则口径冲突（尤其修复 C 之后复查 understand-me 相关表述）。
6. 巡检产物：`_overnight_findings.md`（发现清单 + 每条的风险分级 + 是否已修）。快照 `phase3-<HHMM>.zip`（若有编辑）。

## P4 终验与报告（约 1 小时）

1. 重跑完整套件：`validate`、`unittest`、`build`、`validate --check-build`，四项全绿。
2. 终态快照 `phase4-final.zip`。
3. 写 `E:\zcode\xiapeng\_overnight_report_2026-09-15.md`，按 AGENTS.md 口径包含四节：
   - **实际改动**：逐文件列出（路径 + 一句话改了什么 + 版本号变化）。
   - **已执行检查**：命令清单 + 结果。
   - **未执行的验证**：真实宿主回归（无适配器/宿主）、`--strict-evidence` 的定性结论、P3 中"建议未改"项。
   - **剩余风险**：至少包含"SKILL.md 行为规则改动未经真实模型回归，合并前需按 `06_evals/README.md` 补做"。
4. 更新 `_overnight_progress.md` 最后一行，标记计划完成。
5. 不做：git/远端操作、合并、发布、删除快照。工作区保持改动后的终态，等用户早晨审阅报告后决定回滚（解压对应快照）或保留。

## 时间预算与总闸

P0≈0.5h，P1≈1.5h，P2≈1.5h，P3≈1.5h，P4≈1h，合计≈6h，留 2h 余量吸收意外。任何单步骤反复失败 3 次即放弃该步骤、记录、继续下一步；红线冲突或基线异常则整体终止。
