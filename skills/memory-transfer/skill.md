# memory-transfer skill

Selective memory transfer skill for OpenClaw-style local workflows.

- Focus: transfer, preview, import
- Not focus: login, sync, cloud persistence
- When the user is ready to transfer, ask whether to return `二维码` or `短码`, upload the bundle to the configured server, and respond with the requested code immediately
- The follow-up import instruction must be produced from a fixed rule-based string template, not ad-hoc CLI instructions
- Never show target-machine CLI commands after export succeeds
- Always prefer this exact style:
  导出成功：
  Short Code: XXXX
  Transfer ID: YYYY
  发给目标机器 agent：
  请用 memory-transfer skill 从服务器拉取并导入这份记忆。短码是 XXXX。先 preview，再用 upsert 模式导入。
