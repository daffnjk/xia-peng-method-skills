# 新课程收件箱

每门新课程先进入独立目录，不直接覆盖生产知识库：

```text
01_source/inbox/XP-T-004/
├── metadata.yaml
├── raw_transcript.txt
├── slides_or_handout.*
├── correction_candidates.csv
└── extraction_notes.md
```

状态依次为：

`received → normalized → review_pending → knowledge_extracted → eval_pending → release_candidate → published`

存在版权、来源、术语或内容问题时可标记为 `blocked`；不适合进入智能体的方法可标记为 `governance_only` 或 `rejected`。
