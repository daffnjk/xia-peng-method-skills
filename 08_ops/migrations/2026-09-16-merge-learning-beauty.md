# 合并 main 的 XP-T-005《学习之美》资产并取代 LL 参考路线

日期：2026-09-16。分支：`merge/main-learning-beauty-20260916`（基于 `codex/liulan-learning-candidate`，合入 `main` 3a570a156，即 PR #4）。

## 背景与决定

《学习之美》在本仓库曾有两 条并行接入路线：

1. `codex/liulan-learning-candidate`（2026-09-08，本地草案）：Router 0.4.0 注册 `references/liulan-learning-*` 外部资源（LL-B-001），注册评测 XP-E-075—089。
2. `main` PR #4（2026-09-10，已经审阅合并）：完整来源化 XP-T-005，含 provenance、24 组选段锚点、知识卡 XP-P-049—072、24 道评测 XP-E-075—098 与候选 Skill `book-learning-transfer`。

两条路线的评测 ID 区间重叠（XP-E-075 起），不能共存。本次合并**保留 main 的 XP-T-005 路线**（证据链完整、已经 PR 审阅、时间较新），移除候选分支的 LL 参考路线；候选分支的流水线精简（脚本删除、测试修剪、.gitignore）全部保留。

## 移除的 LL 路线文件

- `.agents/skills/xia-peng-method-router/references/`（liulan-learning-book.md、liulan-learning-practice.md、liulan-learning-source.json）
- `06_evals/learning_reference_evals.jsonl`（XP-E-075—089，与 XP-T-005 评测撞号）
- Router 回退 0.3.1，registry 中 `resources` 清空，METHOD_POLICY 与 SKILL.md 采用 main 措辞

## 保留的历史记录

- `06_evals/candidates/learning-transfer.jsonl`（LL-E-001—015，非运行候选目录，ID 不撞号）
- `08_ops/migrations/2026-09-08-liulan-router.md` 与 `08_ops/liulan-router-PR_DRAFT.md`（历史迁移记录，不改写）
- 被移除文件的完整内容仍可从 `codex/liulan-learning-candidate` 分支找回

## 验证

- `assets.py validate`、`unittest discover`、`assets.py build`、`validate --check-build`：执行后补记于 PR 描述。
- 真实宿主回归：未执行；沿用 PR #4 的结论——24 道新题只是覆盖索引，不证明行为通过。
