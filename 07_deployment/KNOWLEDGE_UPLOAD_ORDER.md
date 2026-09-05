# 知识库上传顺序与实际文件清单

先核对 [来源清单](../01_source/manifest.csv) 的授权范围和目标环境的数据处理要求。不要默认整仓上传：`05_user_private/`、本地评测结果和未经授权的原稿需要分别处理。

## 配置顺序

1. **系统规则**：将 [SYSTEM_PROMPT.md](../03_agent/SYSTEM_PROMPT.md) 放入系统指令，而不是普通知识库。Codex 项目同时使用根目录 [AGENTS.md](../AGENTS.md)。
2. **来源证据**：按 manifest 的 `raw_path` / `reviewed_path` 使用真实文件。当前有四份 `01_source/raw/XP-T-00X_raw.txt`（001—004），只有 `01_source/reviewed/XP-T-004_reviewed.txt` 是带稳定锚点的校对稿；不要构造并不存在的 reviewed 文件路径。
3. **原则与案例**：使用 [principle_cards.yaml](../02_knowledge/principle_cards.yaml) 和 [case_cards.yaml](../02_knowledge/case_cards.yaml)。原则另有 [principle_cards.jsonl](../02_knowledge/principle_cards.jsonl) 表示；选一种经核对的表示，避免重复索引。仓库没有 `case_cards.jsonl`，需要该格式时应显式转换并验证，而不是把文件名当作现成资产。
4. **治理资料**：上传 [claim_audit.yaml](../02_knowledge/claim_audit.yaml)、[contradictions.yaml](../02_knowledge/contradictions.yaml)、[model_registry.yaml](../02_knowledge/model_registry.yaml)。在有争议或高风险主张上主动核查，不把治理层视为可忽略的低优先级资料。
5. **路由与技能**：Codex 使用 `.agents/skills/`；其他平台参考 `04_skills/` 中七个方法论 Skill，并显式配置其中的 `xia-peng-method-router`。文件格式与调用方式由目标平台验证。
6. **个人画像**：仅经用户授权后接入独立上下文，不能混入课程证据库，也不能把模型推断默认为长期事实。

## 引用与验收

原则/案例用于导航，最终结论回查实际原稿；`thinking_map.md` 不替代证据。原稿与校对稿同时索引时保留相同来源 ID、版本和文件角色，避免把同一课程当成两个独立来源。

`XP-T-001`—`003` 的历史段落标号尚需补齐稳定映射，不应当成已经核验的精确引用。接入后运行 [行为评测](../06_evals/README.md)，验证能否检索到实际文件、识别资料缺失并正确执行边界约束。
