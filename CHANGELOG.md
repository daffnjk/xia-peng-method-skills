# Changelog

## Unreleased — 全课程运行时注册与项目说明重构（2026-09-20）

- 将已授权且已完成知识提取的 XP-T-006《职场沟通实讲》和 XP-T-008《情绪管理》正式注册为运行时 Skill：`workplace-communication`、`emotion-management`；XP-T-007 `minimalist-management` 保持已注册。
- Router 升级到 0.4.0，覆盖 XP-T-001—008 的全部已集成来源，并新增沟通、团队管理、情绪管理的复合任务分流。
- 修复公共规则中的状态漂移：原文声称 XP-T-006/008 位于候选区，但实际候选目录并不存在对应 Skill；现在文档、注册表、自动发现目录与运行口径一致。
- 新增注册完整性校验：任何 `knowledge_extracted` 来源如果未被 `xia-peng-method-router` 覆盖，资产校验直接失败，并加入回归测试。
- 重写 README 的项目定位、能力表、课程覆盖、架构、证据边界、新课程上线流程与发布门禁；同步更新 Codex 使用入口。
- XP-T-005 仍按刘澜外部书籍处理；`book-learning-transfer` 保持候选，未因“全部课程上线”而绕过授权或行为验收。
- 本轮不修改课程原稿、reviewed 文本、知识卡事实内容、授权状态或已有评测预期；真实宿主行为回归仍需由 CI/宿主记录确认。

## Unreleased — XP-T-006/007/008 授权与合并 main（2026-09-17）

- 用户于 2026-09-17 会话中明确指示：三门课（XP-T-006/007/008）授权、允许发布、合并 main。manifest 三行 `rights_status` 由 `not_recorded` 改为 `authorized`，并在 notes 记录授权来源与日期；XP-T-001—005 授权状态不变。
- 授权范围与未验证项如实声明：本次为用户明确授权，不代表真实宿主行为回归已运行（XP-E-099—128 共 30 题从未执行）、锚点语义人工复核未做、`release_approval.example.json` 式绑定评分报告哈希的公共发布审批文件未创建（无评分报告可绑定）。发布检查清单中依赖这些证据的项仍未勾选。
- 执行 `feature/xp-t-006-008-courses` → `main` 合并（--no-ff，本地仓库无远端）。

## Unreleased — XP-T-006/007/008 录入审查修复（2026-09-17）

- 审查发现并修复 `minimalist-management` 晋级遗留的过时来源声明（0.2.1→0.2.2）：禁止事项与来源脚注仍写"inbox 暂存未审核、仅文件级定位"，与正文 141 段锚点 reviewed 来源矛盾；统一为 reviewed 文件 + location_checked_not_semantic_verification 口径，脚注措辞与路由（0.3.4）一致。
- 已晋级候选存档 `08_ops/skill_candidates/minimalist-management/SKILL.md` 状态改为 archived 并加存档说明，避免被误认为待审候选；examples.md/change_log.md 按其存档定位保留。
- `03_agent/METHOD_POLICY.md` 来源清单由 5 个补全为 8 个（新增 XP-T-006/007/008 及注册/候选状态说明）；XP-T-004 的段落锚点使用规则扩展至 XP-T-006—008。

## Unreleased — 情绪管理课接入 XP-T-008（2026-09-16）

- 新增来源 `XP-T-008`：《情绪管理》逐字稿（导言、五讲、复习答疑直播），保留原稿并生成 P001—P147 带锚点保守校对稿；约 120 条高置信转写更正记入 correction_log，20 余项存疑词记入 uncertain_terms。
- 新增知识卡：原则 XP-P-104—132（能力与情绪、情绪创可贴、中庸四区与对角线牵拉、三体理论及其三策略、刺激-选择-回应、习得性无助、目标论、社会化与两把剃刀、利他、话语分析等）；模型 XP-M-042—049，并为 SMART/GROW/汉龙剃刀补 XP-T-008 引用；主张审计 XP-CL-030—034（百倍效果、目标治百病、卖房观点等降级处理）；案例 XP-C-022—023。
- 新增题库 `06_evals/emotion_management_evals.jsonl`（XP-E-119—128），覆盖来源归属、适用边界、方法应用、话语分析与重大决策护栏；真实宿主行为回归未运行。
- 新建候选 Skill `08_ops/skill_candidates/emotion-management`，按规则待用户审阅与行为评测，未进入自动发现目录。
- 外部归属：三体理论出自顾及《破圈》，目标论关联阿德勒个体心理学，刺激-选择-回应关联柯维；课程营销段落保留原样。
- 工作区同日另有会话接入 XP-T-006/XP-T-007 的未提交改动；本次编辑避让其 ID 区间（原则 073—103、模型 031—041、案例 020—021、题库 099—118）。

## Unreleased — 工程卫生与版本控制（2026-09-15）

- 符号链接安全用例在无符号链接权限的 Windows 上改为跳过（探测可用性后 skipUnless）；本机测试套件恢复全绿，Linux CI 行为不变。
- 仓库纳入本地 Git 管理：基线提交并打 tag `v0.3.1-baseline`；设置 `core.autocrlf=false` 保护来源哈希锁的字节一致性。未配置远端。
- `OVERNIGHT_PLAN_2026-09-15.md` 顶部标记已执行完毕，防止后续会话按断点续跑指令重做。

## Unreleased — Skill 来源脚注治理（2026-09-15）

- 修复迁移遗留的来源脚注重复：understand-me、goal-management、agent-team-workflow、scene-skill-builder、side-business-system 的重复引用去重。
- 脚注与注册表对齐：side-business-system 补回 XP-T-004 文件级引用；career-planning 补 XP-T-001；xia-peng-method-router 新增覆盖全部登记来源的脚注。
- understand-me 的“每周/每季度”报告措辞改为按需触发，与架构声明的“不自带调度”一致。
- 校验器新增检查：Skill 正文中引用的来源集合必须等于注册表 source_refs 集合；夹具与回归测试同步更新。
- 相关 Skill 版本 0.3.0→0.3.1（router 0.3.1→0.3.2）。仅结构/引用修正，未改方法内容与题库。

## Unreleased — 架构落地（2026-09-05）

- .agents/skills 成为唯一编辑源；JSONL、审阅页、黄金题视图和运行包由构建生成。
- 引用类型拆分；前三个来源的旧段落编号保留在 legacy_source_refs，不再作为有效引用。
- 加入来源哈希锁、JSON Schema、引用/依赖校验、上下文包、行为评测协议和严格发布门禁。
- 课程登记增加前置校验、重复 ID/内容检查、写入锁和普通异常回滚。
- 公共方法规则独立，支持主流程与辅助 Skill、画像私有路径和候选 Skill 审核。
- 新增架构行为题；修正旧题的过期范围与依赖。不宣称模型全量回归已通过。

## Unreleased

- 重写 README，补齐项目定位、七个方法论 Skill、快速开始、来源边界、仓库结构和维护命令。
- 更新 Codex 与平台部署文档，修正不存在的 router、reviewed transcript 和 case JSONL 路径。
- 修订新课程接入示例，避免复用已登记的 XP-T-004；实际来源编号仍以 manifest 为准。
- 新增贡献指南、评测执行说明和项目分析/待办，明确结构检查、脚本测试与模型行为回归的区别。
- Skill 同步改为预检与按文件复制：默认拒绝覆盖已有差异，新增 --check、--dry-run、--force；保留运行目录独有资源，拒绝符号链接和路径类型冲突。
- 新增同步脚本单元测试；扩充发布检查项及 Python、本地评测输出、凭据文件的 Git 忽略规则。
- 未修改课程原稿、知识结论、现有 Skill 内容或题目预期；未宣称已通过全量模型行为回归，未创建新发布版本。

## v0.2.0 — 2026-09-02

- 新增来源 `XP-T-004`：《职业规划》12 讲逐字稿，保留原稿并生成带稳定锚点的保守校对稿。
- 新增职业规划原则、案例、模型、冲突处理与风险主张审计。
- 新建 `career-planning` Skill，覆盖优势识别、试炼、岗位/公司/行业/offer 比较、转岗跳槽、城市、学历和第二曲线。
- Router 与 System Prompt 的材料边界扩展到 `XP-T-004`。
- 新增 12 道职业规划回归评测。
- 对测评定职业、固定年龄阶段、收入承诺、历史公司/行业/城市例子增加了明确护栏。
- 系列、录制日期和对外产品授权仍待用户确认，当前只按内部使用处理。

## v0.1.1 — 2026-08-24

- 增加新课程增量接入 SOP。
- 增加来源清单 `01_source/manifest.csv`。
- 增加新课程登记模板、合并决策表和发布清单。
- 增加新课程收件箱与自动分配 source ID 的脚本。
- 把三份原始逐字稿按稳定 source ID 放入 `01_source/raw/`。
- 核心原则卡、案例卡、System Prompt、Skills 和评测内容未改变。

## v0.1.0 — 2026-08-22

- 建立首版夏鹏智能体方法论知识、Skills、治理和评测资产。
