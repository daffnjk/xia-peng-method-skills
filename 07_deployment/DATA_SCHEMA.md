# 数据契约

可执行契约：`schemas/assets.schema.json`（版本 1.0），由 `assetlib.Catalog` 验证。知识以 YAML 编辑；每条记录的主键为 id，模型使用 model_id；来源清单以 source_id 标识。

引用字段明确区分 source_refs、principle_refs、case_refs、model_refs、claim_refs、conflict_refs、skill_refs。legacy_source_refs 只保留旧编号历史，不是有效引用。支持的有效引用示例：`XP-T-001`（仅文件）和 `XP-T-004#P012-P020`（实际段落）。

来源锁包含 source_version、raw_path、reviewed_path、对应 SHA-256、locator 和定位保证范围；不存在的段落、内容哈希变化或未知状态导致失败。来源锁不是内容正确性、版权或人工审核的证明。

原有知识卡的 evidence_type / confidence 描述主要 statement 的来源支持，不能外推为每个流程步骤、工程护栏或现实效果的验证。外部事实仍需当前核验。

画像事实建议包含 fact_id、value、evidence_source、status、user_confirmed 和有效期；目前由宿主与用户审批维护，不宣称已有独立画像数据库。草案输出在 `05_user_private/drafts/`。

行为评测报告与发布清单都有机器校验的结构。报告记录真实宿主、模型、commit、资产/题库摘要、逐题回答、引用、分数、严重越界和评分依据；发布清单记录白名单文件及摘要。详见 `06_evals/README.md`。
