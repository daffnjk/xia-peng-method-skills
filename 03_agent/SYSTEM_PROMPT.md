# 系统提示词接入入口

公共运行规则唯一来源为 `03_agent/METHOD_POLICY.md`。支持文件读取的宿主应在处理方法论任务前读取它；仅支持粘贴系统提示词的平台，应使用 `python scripts/assets.py build` 生成的 `dist/runtime/03_agent/SYSTEM_PROMPT.md`，其内容是公共规则的完整副本。

不要只粘贴本接入说明后宣称已加载公共规则。Skill 依赖知识和来源文件，应同时接入完整运行包。平台工具、个人资料存储和审批能力需要独立配置；项目不假定平台自动长期记忆。
