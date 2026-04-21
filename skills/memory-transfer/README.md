# memory-transfer skill

This skill is designed for local, file-based demonstrations of agent memory transfer.

这个 skill 用于本地、文件驱动的 agent 记忆迁移演示。

It should be installable on its own. Users should not need to clone the full monorepo just to install the skill.

它应该支持独立安装。用户不应该为了安装这个 skill 而先 clone 整个 monorepo。

The primary installer entrypoint lives at the repository root as `install-skill.sh`, so remote install can use a simple GitHub source.

主要安装入口位于仓库根目录的 `install-skill.sh`，因此远程安装可以直接基于 GitHub 源执行。

## Server Config | 服务端配置

The skill reads backend server config from:

skill 会从以下位置读取 backend 服务地址配置：

- `config.env`: local, ignored by git
- `config.env.example.txt`: committed example

- `config.env`：本地配置文件，已加入 gitignore
- `config.env.example.txt`：提交到仓库的示例文件

Example value:

示例值：

```text
MEMORY_TRANSFER_SERVER_URL=http://127.0.0.1:8000/
```

## Standalone Install | 独立安装

```text
请安装 memory-transfer skill。
安装来源是 GitHub 仓库 `youhan2021/memory-transfer` 的根目录安装脚本 `install-skill.sh`。
安装时请让我输入两项配置：
1. Skill install directory
2. MEMORY_TRANSFER_SERVER_URL
```

During install, the script will ask for `MEMORY_TRANSFER_SERVER_URL` and save it to `config.env`.
It will also ask for the skill install directory, instead of assuming an OpenClaw-only path.

安装过程中，脚本会询问 `MEMORY_TRANSFER_SERVER_URL` 并把它写入 `config.env`。
它还会询问 skill 安装目录，而不是假设只能安装到 OpenClaw 默认路径。

Hermes install prompt:

Hermes 安装 prompt：

```text
请安装 memory-transfer skill。
安装来源是 GitHub 仓库 `youhan2021/memory-transfer` 的根目录安装脚本 `install-skill.sh`。
Skill install directory 请填写 `~/.hermes/skills`。
MEMORY_TRANSFER_SERVER_URL 请按当前环境填写。
```

If the repo is already available locally, you can tell the agent:

如果仓库已经在本地，也可以这样告诉 agent：

```text
请安装当前仓库里的 memory-transfer skill，并在安装时让我输入：
1. Skill install directory
2. MEMORY_TRANSFER_SERVER_URL
```

Supported modes:

支持的安装模式：

```text
- 远程安装仓库里的 skill
- 远程安装并复制 skill
- 本地 link 安装
- 本地 copy 安装
```

## Scripts | 脚本

- `export_memory.py`: export a bundle without automatic filtering, or auto-build one from `.md` / `.txt` memory files
- `create_transfer.py`: upload a bundle and return `short_code + confirm_phrase`
- `lookup_transfer.py`: preview a transfer by short code without exposing full memory content
- `confirm_import.py`: confirm with short code plus confirm phrase, then import locally
- `preview_bundle.py`: summarize a local bundle before import
- `import_memory.py`: import into a local target file or directory
- `apply_import.py`: import mode implementation helper
- `skill_config.py`: reads `config.env` and returns the configured backend server URL

- `export_memory.py`：导出不带自动过滤的 bundle，或从 `.md` / `.txt` 记忆文件自动构建 bundle
- `create_transfer.py`：上传 bundle，并返回 `short_code + confirm_phrase`
- `lookup_transfer.py`：用短码预览 transfer，不暴露完整 memory 内容
- `confirm_import.py`：用短码 + 确认短语完成确认并导入到本地
- `preview_bundle.py`：导入前预览本地 bundle
- `import_memory.py`：导入到本地目标文件或目录
- `apply_import.py`：导入模式实现辅助脚本
- `skill_config.py`：读取 `config.env` 并返回 backend 服务地址

## Repo-Local Install | 仓库内本地安装

```text
请安装当前仓库里的 memory-transfer skill，并在安装时让我输入：
1. Skill install directory
2. MEMORY_TRANSFER_SERVER_URL
```

## Example | 示例

```text
请用 memory-transfer skill 从示例 bundle 导出可迁移记忆。

请用 memory-transfer skill 从 `memory` 目录直接生成 bundle 并导出可迁移记忆。

请用 memory-transfer skill 从 `2026-04-18-moyu-threebody.md` 直接生成 bundle，并创建 transfer session。

请用 memory-transfer skill 使用短码 lookup 这份记忆，只展示 preview。

请在 preview 之后要求我输入 confirm phrase，再用 upsert 模式完成导入。
```
