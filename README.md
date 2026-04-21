# memory-transfer

`memory-transfer` is a low-friction MVP for selective agent memory export and import. It is intentionally not an account system, not a sync engine, and not a long-term cloud storage product. The goal is a minimal `export -> lookup preview -> confirm import` loop built around short codes plus confirm phrases and a temporary relay backend.

`memory-transfer` 是一个低摩擦的 agent 记忆导出与导入 MVP。它不是账户系统，不是同步引擎，也不是长期云存储产品。目标是提供一个最小化的 `export -> lookup preview -> confirm import` 闭环，并基于短码 + 确认短语与临时中转后端完成配对。

## Project Goal | 项目目标

This repo contains:

- A Python + FastAPI backend for temporary bundle relay
- An OpenClaw-style skill package focused on memory transfer
- Shared schemas, examples, and protocol docs
- A repo-level install flow for contributors
- A standalone skill install flow for end users

这个仓库包含：

- 一个基于 Python + FastAPI 的临时 bundle 中转后端
- 一个聚焦记忆迁移的 OpenClaw 风格 skill 包
- 共享 schema、示例和协议文档
- 面向开发者的仓库级安装流程
- 面向最终用户的独立 skill 安装流程

## Install Modes | 安装方式

There are two install paths:

- `skill-only install`: for users who only need the OpenClaw/Hermes skill
- `repo/dev install`: for contributors who want backend, docs, tests, and skill together

目前有两种安装路径：

- `skill-only install`：只需要 OpenClaw/Hermes skill 的用户
- `repo/dev install`：需要 backend、文档、测试和 skill 的开发者

### Skill-Only Install | 仅安装 Skill

The skill is intended to be installable on its own, without cloning the full monorepo.

这个 skill 设计为可独立安装，不要求用户先 clone 整个 monorepo。

Recommended install prompt:

推荐安装 prompt：

```text
请安装 memory-transfer skill。
安装来源是 GitHub 仓库 `youhan2021/memory-transfer` 的根目录安装脚本 `install-skill.sh`。
安装时请让我输入两项配置：
1. Skill install directory
2. MEMORY_TRANSFER_SERVER_URL
```

If you want Hermes-style install, use this prompt:

如果你要安装到 Hermes，可使用下面这段 prompt：

```text
请安装 memory-transfer skill。
安装来源是 GitHub 仓库 `youhan2021/memory-transfer` 的根目录安装脚本 `install-skill.sh`。
Skill install directory 请填写 `~/.hermes/skills`。
MEMORY_TRANSFER_SERVER_URL 请按当前环境填写。
```

If you already cloned this repo locally, ask the agent to run the local skill installer and let you input:

如果你已经在本地 clone 了仓库，可以让 agent 使用本地安装器，并允许你输入：

```text
请安装当前仓库里的 memory-transfer skill，并在安装时让我输入：
1. Skill install directory
2. MEMORY_TRANSFER_SERVER_URL
```

Supported skill install modes:

支持的 skill 安装模式：

```text
- 远程安装仓库里的 skill
- 远程安装并复制 skill
- 本地 link 安装
- 本地 copy 安装
```

That installer only does one thing:

- install the `memory-transfer` skill into your local runtime skills directory

这个安装器只做一件事：

- 将 `memory-transfer` skill 安装到本地运行时 skills 目录

Default target:

默认目标目录：

```text
~/.openclaw/skills/memory-transfer
```

### Repo / Dev Install | 仓库 / 开发安装

Use the repo-level installer only when you want the backend and local development environment too:

只有在你需要 backend 和本地开发环境时，才使用仓库级安装器。

Recommended backend install prompt:

推荐 backend 安装 prompt：

```text
请安装当前仓库的 backend 开发环境。
请使用仓库根目录的 `install-backend` 安装器完成依赖安装和运行目录初始化。
```

The repo installer will:

- check for `python3`
- ensure `uv` is available
- sync backend dependencies with `uv`
- create runtime directories
- install the `memory-transfer` skill into your local runtime skills directory

仓库安装器会执行：

- 检查 `python3`
- 确保 `uv` 可用
- 用 `uv` 同步 backend 依赖
- 创建运行时目录
- 把 `memory-transfer` skill 安装到本地运行时 skills 目录

Supported repo install modes:

支持的仓库安装模式：

```text
- 标准 backend 安装
- link 模式 backend 安装
- copy 模式 backend 安装
- dev 模式 backend 安装
```

## Backend | 后端

Start the backend with:

启动 backend：

```text
请启动 memory-transfer backend 开发服务。
如果需要自动同步依赖并启动本地 FastAPI 服务，请使用仓库里的 backend 开发启动流程。
```

Or directly:

或者告诉 agent：

```text
请在 backend 目录启动本地开发服务，并确保依赖已经通过 uv 同步完成。
```

Available MVP endpoints:

当前 MVP API：

- `GET /health`
- `POST /transfer/create`
- `POST /transfer/lookup`
- `POST /transfer/confirm-import`

## Skill Install Location | Skill 安装位置

Both installers resolve the skill destination in this order:

两个安装器都会按下面顺序解析 skill 安装目录：

- `$OPENC LAW_SKILLS_DIR` when set exactly as that environment variable name
- otherwise `$OPENCLAW_SKILLS_DIR` when set
- otherwise `~/.openclaw/skills`

Default installed path:

默认安装路径：

```text
~/.openclaw/skills/memory-transfer
```

## Basic Flow | 基本流程

1. Export memories from a source file
2. Create a transfer session with `POST /transfer/create`
3. Share the returned `short_code` and `confirm_phrase`
4. On the target side, call `POST /transfer/lookup` with the short code
5. Show preview only and ask for the confirm phrase
6. Call `POST /transfer/confirm-import` with `short_code + confirm_phrase`

1. 从源文件导出记忆
2. 通过 `POST /transfer/create` 创建 transfer session
3. 分享返回的 `short_code` 和 `confirm_phrase`
4. 在目标端用短码调用 `POST /transfer/lookup`
5. 只展示 preview，并要求用户输入确认短语
6. 用 `short_code + confirm_phrase` 调用 `POST /transfer/confirm-import`

## Uninstall Or Reinstall | 卸载或重装

Remove the installed skill directory:

删除已安装的 skill 目录：

```text
请删除本地已安装的 memory-transfer skill 目录。
```

Reinstall the skill only:

仅重装 skill：

```text
请重新安装 memory-transfer skill。
安装来源仍然使用仓库根目录的 `install-skill.sh`，并在安装时让我输入配置。
```

Reinstall the whole repo dev setup:

重装整个 repo 开发环境：

```text
请重新安装当前仓库的 backend 开发环境，并使用 link 模式。
```

If you want a clean backend environment:

如果你想清理 backend 环境：

```text
请清理当前仓库的 backend 本地环境，然后重新执行 backend 安装流程。
```
