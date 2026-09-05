# 贡献与维护指南

本项目以可追溯的方法论资产为核心。贡献可以是文档修订、来源补强、知识审计、Skill 改进或维护脚本测试；不以增加文件数量代替证据质量。

## 开始前

先读 [AGENTS.md](AGENTS.md)、[项目分析](08_ops/PROJECT_REVIEW.md) 和与任务相关的来源。使用独立分支，保持改动范围清晰；不修改课程原稿、不补造缺失模型、不把个人资料当课程证据。

来源授权以 [manifest](01_source/manifest.csv) 为准。提交课程、图片或第三方 Skill 前核对来源、授权范围和署名要求；不要因仓库可访问就推定可公开分发。当前没有为全部内容统一新增开源许可证，授权范围需由维护者确认。

## 各类修改的同步范围

| 修改类型 | 一起检查或更新 |
| --- | --- |
| 文档、目录或命令 | README、Codex 指南、相关部署/运维文档中的链接和示例 |
| 新课程 | manifest、原稿/校对稿、纠错记录、知识资产、必要的边界/路由、评测、变更记录 |
| 原则或案例 | 来源 ID、证据等级、冲突/风险审计、对应评测；原则 YAML 与 JSONL 表示的一致性 |
| 共享方法论 Skill | `04_skills/<name>/` 与 `.agents/skills/<name>/`、相关场景题和边界题 |
| 仅 Codex 使用的辅助 Skill | `.agents/skills/<name>/`，保留第三方来源元信息，不假定必须加入兼容目录 |
| Python 维护脚本 | 使用说明、错误与退出码行为、标准库单元测试 |

七个现有共享方法论 Skill 优先在 `04_skills/` 修改后同步。同步是单向复制，不是自动双向合并；`--force` 也不会删除运行目录独有资源。删除、重命名和废弃 Skill 应在 PR 中单独说明并人工处理。

## 本地检查

在仓库根目录运行，建议 Python 3.10+：

```bash
python3 scripts/verify_codex_setup.py
python3 scripts/sync_codex_skills.py --check
python3 -m unittest discover -s tests -v
git diff --check
git status --short
```

文档改动需核对相对链接、示例路径和命令参数。维护脚本测试使用临时目录，不接触真实课程或个人资料。设置检查只覆盖文件存在和基础 Skill 元信息，尚不覆盖完整 YAML/JSONL 模式、跨文件引用或来源锚点有效性。

改动规则、Skill 或知识后，按 [评测说明](06_evals/README.md) 运行相关行为题；发布前按 [发布清单](08_ops/RELEASE_CHECKLIST.md) 完成全量行为回归。没有执行的检查必须明确写为“未运行”，不得把测试计划写成已通过。

## PR 说明应包含

说明修改动机、涉及文件、证据或工程化外推的边界、检查命令与结果，以及已知限制。新增来源或改变行为时列出相关来源/卡片/评测 ID；涉及脚本覆盖语义时说明迁移方式和回退方案。

更新 [CHANGELOG.md](CHANGELOG.md) 的 `Unreleased` 部分；维护者确认发布前，不创建虚构的发布版本或替换历史版本记录。`CHANGELOG_CODEX.md` 保留既有适配历史，新维护记录集中在主变更日志。

## 隐私与发布

真实简历、周报、组织信息、API 密钥与模型回答日志不得出现在示例、测试或 PR 中。`05_user_private/` 除 README 外默认忽略，但 Git 忽略规则不是访问控制，不能删除已经提交的内容。行为评测输出默认放入被忽略的 `06_evals/results/`，需要共享时先脱敏并确认授权。

课程接入细则见 [SOP](08_ops/INCREMENTAL_INGESTION_SOP.md)；来源冲突按 [合并决策表](08_ops/MERGE_DECISION_MATRIX.md) 处理，禁止静默覆盖旧观点。
