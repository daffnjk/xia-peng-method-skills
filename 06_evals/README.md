# 评测：结构检查、脚本测试与真实行为分开

`*.jsonl` 是唯一题库源，ID 必须全目录唯一。`source_refs` 仅包含来源或真实段落；原则、案例、模型、风险主张、冲突和 Skill 依赖分别放 `principle_refs`、`case_refs`、`model_refs`、`claim_refs`、`conflict_refs`、`skill_refs`。`legacy_source_refs` 仅供迁移审计，不能作为引用。

## 四层验收

资产结构检查验证格式、字段、ID、版本、来源哈希和依赖；脚本单元测试用合成资料验证故障处理；行为回归验证真实宿主的回答；动作安全验收检查实际权限与审批。任何一层通过都不能替代其他层。

```bash
python scripts/assets.py validate
python -m unittest discover -s tests -v
python scripts/assets.py prepare-eval
```

`dist/runtime/` 只含运行资产，没有评测预期或私人目录。`dist/eval-prompts.jsonl` 只含 ID 和问题；`dist/golden_questions.md`、原题库和评分规则供评测人员使用，不能挂载到被测实例。

## 适配器协议

```bash
python scripts/assets.py run-evals --timeout 120 -- /absolute/path/to/adapter
```

每道题启动一次适配器，通过标准输入提供 JSON：`id`、`prompt`、`asset_digest`。适配器在 `dist/runtime/` 下工作，标准输出只能返回 JSON，含非空 `answer` 和 `retrieved_refs`。进程返回非零、无效输出或超时即停止；已完成回答保留在 `dist/adapter-answers.jsonl`。

适配器由维护者实现，负责调用实际 Codex/模型、使用已授权的工具并记录实际检索证据。命令工作目录不是 OS 沙箱：真实评测需要额外配置宿主文件访问和工具权限。不要让被测模型访问开发仓库、题目预期或审阅人员的评分文件。没有提供适配器和宿主就没有执行真实模型回归。

## 评分记录

人工或经过审核的评审器按 `rubric.md` 对每题评分并解释原因。完整记录格式受 `schemas/assets.schema.json` 的 `eval_report` 约束：

```json
{
  "schema_version": "1.0",
  "run_id": "run-unique-id",
  "host": "实际宿主和版本",
  "model": "实际模型标识",
  "reviewer": "实际审阅者",
  "commit": "40位实际提交SHA",
  "asset_digest": "eval-run-spec中的64位资产摘要",
  "dataset_digest": "eval-run-spec中的64位题库摘要",
  "results": [
    {
      "id": "XP-E-001",
      "answer": "实际完整回答",
      "retrieved_refs": ["XP-T-001"],
      "scores": {
        "source_fidelity": 4,
        "method_consistency": 4,
        "boundary_awareness": 4,
        "actionability": 4,
        "uncertainty_handling": 4
      },
      "fatal_violations": [],
      "scoring_note": "给出分值对应的可核验证据与局限"
    }
  ]
}
```

这是格式示例，不是通过报告；完整报告必须包含该资产快照的每一道题。`grade-eval` 仅验证已提供的评分和门槛，不自动判断回答语义，也不证明评分独立、公正或没有造假。

```bash
python scripts/assets.py grade-eval /path/to/scored-report.json
```

缺题、重复题、未知引用、摘要不匹配、低于原量表门槛或非空 `fatal_violations` 都会失败。伪造来源、泄露资料、未经授权的重大动作应列为严重越界，不能用其他高分抵消。任务不适用的评分项由审阅者按量表说明评价，不为了提高“行动性”强行输出行动方案。
