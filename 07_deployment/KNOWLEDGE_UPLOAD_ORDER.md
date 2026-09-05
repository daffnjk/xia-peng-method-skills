# 知识库上传顺序

1. `03_agent/SYSTEM_PROMPT.md`：放入系统指令，不放知识库。
2. `01_source/XP-T-00X_reviewed.md`：放入原始证据库。
3. `02_knowledge/principle_cards.jsonl` 与 `case_cards.jsonl`：放入高优先级检索库。
4. `02_knowledge/claim_audit.yaml`、`contradictions.yaml`、`model_registry.yaml`：放入治理库。
5. `04_skills/*/SKILL.md`：作为可调用技能或独立工作流。
6. 用户自己的资料必须进入独立的用户画像库，不能混入夏鹏方法论知识库。

建议检索排序：原则卡/案例卡 > 原始逐字稿 > 治理文件；最终回答前再回查逐字稿。
