# 项目工程规则

## 任务边界

这是非官方方法论资产库，不是夏鹏本人或独立应用服务。方法论任务先读取 `03_agent/METHOD_POLICY.md`，包括显式调用单个 Skill。工程修改先读取本文件、`08_ops/ARCHITECTURE.md` 和受影响文件，不需要把完整课程灌入上下文。

## 编辑与证据

- `.agents/skills/` 是唯一 Skill 编辑源；`02_knowledge/*.yaml` 是知识源；`06_evals/*.jsonl` 是题库源。
- `dist/` 是生成物，不编辑、不提交。`04_skills/` 不得反向同步。
- 原始课程保持只读；新版本原稿必须保留旧证据并经审阅更新来源锁，不静默覆盖或自动刷新哈希掩盖变化。
- XP-T-001—003 不具备已核验段落映射，禁止创建或复用其旧 `#Pxxx`。历史编号只可存于 `legacy_source_refs` 审计字段。
- 公共方法论规则只修改 `03_agent/METHOD_POLICY.md`；根目录系统提示词是接入说明，不是第二份规则源。
- 用户资料固定在 `05_user_private/`，问答默认只读。候选 Skill 放在 `08_ops/skill_candidates/`，未经审批不进入自动发现目录。

## 验证命令

```bash
python -m pip install -r requirements-dev.txt
python scripts/assets.py validate
python -m unittest discover -s tests -v
python scripts/assets.py build
python scripts/assets.py validate --check-build
```

涉及行为规则、Skill、知识或题库时，还须按 `06_evals/README.md` 做真实宿主回归；测试合成适配器不是模型验收。不要把题目预期放入被测模型可访问目录。

## 修改完成时

报告实际改动、执行过的检查、没有执行的验证及剩余风险；保留来源与数据迁移记录。未确认的授权、模型评分或人工审批不得补造。改动使用分支和 PR，不自动合并、对外发布或执行用户的重大职业/财务决定。
