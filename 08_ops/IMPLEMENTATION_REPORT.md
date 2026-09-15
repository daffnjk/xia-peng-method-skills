# 架构落地与验收记录

日期：2026-09-05。范围：将原有方法论资产库升级为有唯一维护源、机器校验、可重复构建和评测接口的仓库；不建设多用户在线服务。

## 实施基线

- 主分支基线：`d28a69acc5950ef1ec161021098fda7d62b9a7bb`。
- 继承 README/维护改进提交：`3a6cbeb2d83f81250e04f0beabd3d20d5f88b6b0`（PR #1）。
- 完整仓库迁移在独立 GitHub Actions 工作区执行，成功结果提交为 `b9312f59d5ff73436f10821b031d6c7d6001f3f1`。
- 最终功能分支使用清理后的同一实现树，不继承临时传输和诊断提交。永久 CI 仅有只读权限；临时迁移工作流不进入最终 PR。

## 已实现

| 目标 | 实现 |
| --- | --- |
| 唯一维护源 | `.agents/skills/` 为唯一 Skill 源；知识维护 YAML；题库维护 JSONL；公共运行规则集中到 `03_agent/METHOD_POLICY.md`。删除旧的重复 Skill 与独立维护的原则 JSONL，保留迁移入口。 |
| 数据契约与引用 | JSON Schema、重复键/ID、字段/枚举、来源锁、实际段落、分类型依赖及循环检查；设置检查入口升级为完整资产检查。 |
| 构建与分发 | `assets.py build` 单向生成内部运行目录/ZIP、索引、原则 JSONL、黄金题视图、HTML 审阅页及哈希清单；检查目录和 ZIP 的成员及字节。 |
| 治理与组合 | 注册主 Skill 和可选辅助依赖；`context` 返回本地知识与同来源治理信息；不宣称是语义检索、调度器或权限沙箱。 |
| 课程登记 | 写入前校验、全局 ID 和稿件去重、独占锁、临时写入、manifest 提交点、普通异常回滚；保留强制终止时的人工恢复边界。 |
| 评测与门禁 | 增加 12 条架构行为题；提供不传标准答案的适配器接口、超时/失败处理、完整评分报告校验及资产/题库摘要绑定。公开构建要求严格证据、授权、命名审批和同版本报告。 |
| 文档与自动检查 | 更新 README、Codex 指南、部署、接入、发布、贡献、架构与变更说明；增加 Python 3.11/3.13 PR CI。 |

## 证据迁移细节

XP-T-001—003 没有经过核对的历史段落映射。旧编号归档为 `legacy_source_refs`，当前有效引用明确降为文件级；不得把这种降级描述为“精确证据已经补齐”。严格模式仍会拒绝相关资产。

XP-T-004 的校对稿共有 578 个实际标记，编号最高到 592。14 个空白物理行没有标记：37、74、117、171、217、283、297、353、387、423、467、504、546、568。

迁移器只有在确认所有现有标记等于物理行号、范围端点真实存在、缺号位置确实为空行时，才把跨空行范围拆为连续的实际标记区间。非空缺号、缺失端点或未知编号规则仍报错。原引用与拆分结果记录在 [迁移账本](migrations/2026-09-05-architecture.json) 的 `verified_range_splits` 中。**没有修改原稿或校对稿字节，没有新造段落号，没有放宽范围校验器。**

## 已执行的工程验收

[完整仓库迁移与验证运行](https://github.com/daffnjk/xia-peng-method-skills/actions/runs/33949842426) 的日志记录：

- `assets.py validate` 通过：4 个来源、7 个运行 Skill、48 条原则、19 个案例、29 个主张、13 个冲突、29 个模型、74 条行为评测题。
- `python -m unittest discover -s tests -v`：79/79 通过，无跳过。它们是合成资料驱动的工程测试，不是 79 次真实模型调用。
- 完整资产构建与 `validate --check-build` 通过；相同输入重复构建后 `dist/runtime.zip` 的 SHA-256 相同。
- `prepare-eval` 成功生成隔离运行包和仅含题目的输入；真实模型没有被调用。
- `validate --strict-evidence` 与 `build --public` 均按预期拒绝当前不满足精确证据的资产。该运行首先命中证据阻断，不宣称已完成授权或语义审核。
- Python 编译和 Git 空白检查通过；暂存文件检查确认 `01_source/raw/`、`01_source/reviewed/`、`05_user_private/` 没有修改。

永久 PR CI 在最终提交上重新检查，结果以对应 PR Checks 为准，不把本记录当作未来提交自动通过的证明。

## 未完成且不得伪造的审核

前三份来源的精确人工映射、所有材料与第三方资产的再分发授权、真实宿主/模型全量语义评测、实际工具权限隔离仍需单独确认。评分器验证评分记录，不替代人或经过校准的评审器判断语义；工作目录隔离不等于操作系统沙箱。

没有修改课程实质结论，没有替用户确认授权，没有发布公共课程包，没有创建稳定版发布标签，也没有合并到 main。

## 使用与回退

```bash
python -m pip install -r requirements-dev.txt
python scripts/assets.py validate
python -m unittest discover -s tests -v
python scripts/assets.py build
python scripts/assets.py validate --check-build
```

新用户直接使用已经迁移的分支，无需重复执行一次性迁移器。后续流程见 [架构说明](ARCHITECTURE.md)、[接入 SOP](INCREMENTAL_INGESTION_SOP.md) 与 [评测说明](../06_evals/README.md)。回退通过 Git revert/已确认的旧 commit，不从 dist 反向覆盖源文件。
