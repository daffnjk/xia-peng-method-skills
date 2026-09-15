# 知识接入顺序

先运行 `python scripts/assets.py build`。只使用 `dist/runtime/` 的同一份构建，不混用不同版本文件。

1. 将生成的 `03_agent/SYSTEM_PROMPT.md` 放入宿主系统指令。
2. 加载 `03_agent/skill_registry.json` 与 `.agents/skills/` 中的注册 Skill。
3. 原稿/校对稿与 source_locks 提供证据定位；知识 YAML、生成的原则 JSONL 和 index 提供检索入口。
4. 关联加载 claim_audit、contradictions 与 model_registry，不能只检索正向原则而漏掉限制。
5. 用户资料使用独立授权存储；不要上传整个开发仓库或 05_user_private。

运行包不含评测预期；开发目录下的题库、golden_questions 展示和测试资料不得提供给被测模型。平台是否支持原生 Skills、文件解析、工具权限和长期状态要独立验证，不能从文件存在推断。
