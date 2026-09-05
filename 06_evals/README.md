# 评测执行说明

[返回首页](../README.md) · [评分量表](rubric.md) · [黄金题](golden_questions.md) · [JSONL 题库](evals.jsonl)

## 三种检查不能混用

| 检查 | 执行方式 | 可以证明什么 |
| --- | --- | --- |
| 项目基础检查 | `python3 scripts/verify_codex_setup.py` | 必要文件存在，预期 Skill 的基础元信息可识别 |
| 同步与脚本回归 | `python3 scripts/sync_codex_skills.py --check`；`python3 -m unittest discover -s tests -v` | 同步源文件的对应副本一致；维护脚本在测试场景下符合预期 |
| 模型行为回归 | 在目标 Codex/智能体环境执行题库，按量表审阅答案 | 来源忠实度、方法一致性、边界意识、行动性与不确定性处理 |

以上命令从仓库根目录运行。基础检查不会调用模型，也不完整解析 YAML/JSONL 或核对所有来源锚点。仓库目前没有自动调用模型、逐题评分并汇总通过率的评测运行器；存在题库不等于已经执行或通过回归。

## 题目结构

`evals.jsonl` 每行一题，包含 `id`、`category`、`prompt`、`expected_behavior`、`source_refs`、`forbidden_behavior` 和 `score_dimensions`。`golden_questions.md` 用于人工阅读，评分口径以 `rubric.md` 为准。

## 执行流程

1. 记录仓库 commit、日期、宿主及版本、实际模型、规则/Skill 版本、可用工具和检索配置。关闭无关个人画像，或明确记录本次授权使用的上下文。
2. 将 `prompt` 原样交给目标智能体。除非题目本身需要多轮对话，使用独立会话，避免把上一题答案或 `expected_behavior` 提供给模型。
3. 保存实际回答、检索证据和可核验的文件位置。评分者再对照预期行为、禁止行为和原稿审阅；不得只凭措辞像不像预期判断通过。
4. 按五个维度分别打 1—5 分。每题通过要求为总分至少 **20/25**，且**来源忠实度、边界意识均不低于 4 分**。报告每题结果和失败原因，不以平均分掩盖关键失败。
5. 修复失败项后重跑相关题。准备发布时运行全部新旧题；抽样只能标为抽样，不能宣称“全量回归通过”。未解决的关键来源或边界失败应阻止发布。

上述逐题记录和发布门槛是工程维护约定，不是课程原话。执行过程可能产生模型服务费用，具体由所选宿主和账户决定；维护脚本单元测试不调用模型。

## 来源引用的已知限制

`XP-T-004` 有 `01_source/reviewed/XP-T-004_reviewed.txt` 中的稳定段落锚点。`XP-T-001`—`003` 的知识卡和题库中保留了历史 `#Pxxx` 引用，但当前项目规则明确其 raw 稿尚无稳定锚点；不能据此宣称这些引用已能精确定位。

评测时根据 [manifest](../01_source/manifest.csv) 回查实际原稿路径，记录短摘录或可复现的定位线索。找不到对应内容时标为“来源待核验”，不能伪造段落编号，也不能跳过来源维度后判为通过。补齐锚点映射属于单独的证据整理任务，不应在普通文档更新中猜测修复。

## 结果记录

建议将实际结果存入本地 `06_evals/results/`（默认 Git 忽略）。每次执行至少记录：

```text
run_id / executed_at / repository_commit
host_version / model / instruction_version / retrieval_config
eval_id / actual_answer / evidence_paths
source_fidelity / method_consistency / boundary_awareness
actionability / uncertainty_handling / total / passed
reviewer / failure_reason / follow_up
```

不要在仓库中提交真实个人资料、密钥、未经授权的课程长摘录或包含这些信息的回答日志。只添加了题目、只审阅了文件或只跑了单元测试时，分别记录实际完成事项，模型行为状态写为“未运行”。
