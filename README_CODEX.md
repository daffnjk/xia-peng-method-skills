# 在 Codex 中使用

在完整仓库根目录运行 `python -m pip install -r requirements-dev.txt`，然后执行 `python scripts/assets.py validate`。在 Codex 中打开同一目录；项目规则见 `AGENTS.md`，方法论公共规则见 `03_agent/METHOD_POLICY.md`，可发现的 Skill 位于 `.agents/skills/`。

首次任务建议：

```text
阅读项目规则与公共方法规则，说明已接入来源、引用限制和可用 Skill。不修改文件。
```

```text
$career-planning
基于我本次授权的资料，比较现岗调整和跳槽。区分事实、自述、推断与缺口，给可逆试炼和停止条件，不代替我批准离职。
```

```text
$goal-management
确认本月目标的指标口径、基线和资源，再拆路径。已有信息不重复追问；外部数字未核验时不要假装已查证。
```

画像草案只放 `05_user_private/drafts/`，未经确认不更新正式画像。新 Skill 先放 `08_ops/skill_candidates/`。Codex 的实际文件权限、网络权限和审批策略由宿主设置决定，Git 忽略不提供访问控制。

## 维护模式

直接编辑 `.agents/skills/`；不要编辑 `04_skills/` 再同步。校验使用 `python scripts/assets.py validate`，导出使用 `python scripts/assets.py build`。

方法规则、知识或 Skill 变更后，除单元测试外还要执行真实宿主评测。被测实例仅挂载 `dist/runtime/`，题目通过 `dist/eval-prompts.jsonl` 逐条输入；不要把开发仓库及其标准答案一并挂载。宿主负责模型调用、权限隔离和实际回答记录。

平台安装与界面会变化，以 OpenAI 官方 Codex 文档为准：<https://developers.openai.com/codex/>。
