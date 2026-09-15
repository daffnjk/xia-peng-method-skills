# 新课程增量接入 SOP

原稿登记 → 保守校对 → 提取候选 → 差异/冲突审阅 → 确认引用与来源锁 → 必要的 Skill 更新 → 静态与真实行为评测 → 审批发布。不要将 inbox 中的整份新稿直接作为已审核知识。

## 1. 登记与授权

至少提供 UTF-8 文本稿、标题、系列/顺序及使用范围；未知录制日期留空，不猜测。脚本只创建暂存资产和 manifest 的 received 行，不自动把它视为可用证据。

```bash
python scripts/scaffold_new_course.py --title "新课标题" --transcript /path/to/transcript.txt
```

ID 以 manifest 和现有来源目录自动递增，不能复用 XP-T-004。相同 ID 或同一稿件内容拒绝重复登记。同一课程修订走 source_version，不假装新课程。输入二进制文档应先人工确认提取为文本。

## 2. 校对与切片

原稿只读保留；高置信度校对写新 reviewed 文件，存修订记录；不确定词放 uncertain_terms。按完整语义设置稳定锚点，已发布锚点不重新编号。真实新来源可使用 `[XP-T-005#P001]` 这样的形式，此处是格式示例，不表示该课程已接入。

## 3. 知识审阅

按 MERGE_DECISION_MATRIX.md 区分重复、补强、条件变化、冲突、新方法和风险主张。来源忠实度不等于实证有效性。更改知识 YAML，不手工同步第二份 JSONL。来源与知识/Skill 依赖使用各自类型字段。

## 4. 进入已接入状态

把核对后的原稿与校对稿分别放入 raw/reviewed，更新 manifest 路径、source_version 和 knowledge_extracted 状态。由审阅者核对原始字节和稳定锚点后填写 source_locks.json，记录两个文件的 SHA-256 与 locator；无精确段落则只能选 file_only。不得用“重算锁”掩盖未经审核的原稿变化。

历史 `legacy_source_refs` 是只读迁移记录。解决它需要逐条核验后更新有效引用；不能再将这些编号直接复制到有效 source_refs。

## 5. 更新方法与评测

只有行为范围发生变化时才更新公共规则、注册表或 Skill。新 Skill 先放 `08_ops/skill_candidates/`，经审核再启用；增加来源复现、迁移、边界与冲突题。方法论 Skill 引用共享规则并保留用户审批点。

```bash
python scripts/assets.py validate
python -m unittest discover -s tests -v
python scripts/assets.py build
python scripts/assets.py validate --check-build
```

然后按 06_evals/README.md 在隔离运行包中做真实宿主全量回归。不能把这些静态命令说成模型已经回答正确。

## 6. 发布与恢复

记录资产摘要、实际验证、兼容性和回退 commit。公共发布另需授权、精确证据、行为报告和人工审批。任何缺失都不能猜测填写。

登记出现普通异常可在原因修复后重试；遇到遗留 `.ingestion.lock`，先确认无活动进程，再核对 manifest 和 intake。若 manifest 没有对应行，确认暂存是本次失败残留后再清理；若已有行和完整文件，应按已提交状态处理，不能再分配同一 ID。断电/强制终止不承诺自动恢复。
