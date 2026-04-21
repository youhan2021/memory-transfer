#!/usr/bin/env bash
set -euo pipefail

REPO_SLUG="${MEMORY_TRANSFER_REPO:-youhan2021/memory-transfer}"
REPO_REF="${MEMORY_TRANSFER_REF:-main}"
MODE="copy"
SERVER_URL="${MEMORY_TRANSFER_SERVER_URL:-}"
DEFAULT_SERVER_URL="http://127.0.0.1:8000/"
SKILLS_DIR_INPUT="${MEMORY_TRANSFER_SKILLS_DIR:-${OPENCLAW_SKILLS_DIR:-}}"

resolve_skills_dir() {
  if [[ -n "${SKILLS_DIR_INPUT}" ]]; then
    printf '%s\n' "${SKILLS_DIR_INPUT}"
    return
  fi

  local openc_law_dir=""
  openc_law_dir="$(printenv 'OPENC LAW_SKILLS_DIR' 2>/dev/null || true)"
  if [[ -n "${openc_law_dir}" ]]; then
    printf '%s\n' "${openc_law_dir}"
    return
  fi

  if [[ -n "${OPENCLAW_SKILLS_DIR:-}" ]]; then
    printf '%s\n' "${OPENCLAW_SKILLS_DIR}"
    return
  fi

  printf '%s\n' "${HOME}/.openclaw/skills"
}

usage() {
  cat <<EOF
Usage:
  ./install-skill.sh
  ./install-skill.sh --copy
  ./install-skill.sh --link
  ./install-skill.sh --skills-dir <path>
  ./install-skill.sh --server-url <url>
  ./install-skill.sh --ref <git-ref>
  ./install-skill.sh --repo <owner/repo>

Environment:
  MEMORY_TRANSFER_REPO   Override GitHub repo, default: ${REPO_SLUG}
  MEMORY_TRANSFER_REF    Override git ref, default: ${REPO_REF}
  MEMORY_TRANSFER_SERVER_URL  Preseed the backend server URL for config.env
  MEMORY_TRANSFER_SKILLS_DIR  Preseed the skill install directory

Notes:
  - copy mode works both locally and from a remote raw GitHub URL
  - link mode only works from a local checkout
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy)
      MODE="copy"
      shift
      ;;
    --link)
      MODE="link"
      shift
      ;;
    --server-url)
      SERVER_URL="${2:?missing value for --server-url}"
      shift 2
      ;;
    --skills-dir)
      SKILLS_DIR_INPUT="${2:?missing value for --skills-dir}"
      shift 2
      ;;
    --ref)
      REPO_REF="${2:?missing value for --ref}"
      shift 2
      ;;
    --repo)
      REPO_SLUG="${2:?missing value for --repo}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_SKILL_DIR="${SCRIPT_DIR}/skills/memory-transfer"

prompt_skills_dir() {
  if [[ -n "${SKILLS_DIR_INPUT}" ]]; then
    return
  fi

  if [[ ! -t 0 ]]; then
    SKILLS_DIR_INPUT="${HOME}/.openclaw/skills"
    return
  fi

  printf 'Skill install directory [%s]: ' "${HOME}/.openclaw/skills"
  read -r input_dir
  SKILLS_DIR_INPUT="${input_dir:-${HOME}/.openclaw/skills}"
}

prompt_server_url() {
  if [[ -n "${SERVER_URL}" ]]; then
    return
  fi

  if [[ ! -t 0 ]]; then
    SERVER_URL="${DEFAULT_SERVER_URL}"
    return
  fi

  printf 'MEMORY_TRANSFER_SERVER_URL [%s]: ' "${DEFAULT_SERVER_URL}"
  read -r input_url
  SERVER_URL="${input_url:-${DEFAULT_SERVER_URL}}"
}

write_config_env() {
  local target_dir="$1"
  cat > "${target_dir}/config.env" <<EOF
MEMORY_TRANSFER_SERVER_URL=${SERVER_URL}
EOF
}

install_from_local() {
  local target_root target_dir
  target_root="$(resolve_skills_dir)"
  target_dir="${target_root}/memory-transfer"

  mkdir -p "${target_root}"
  rm -rf "${target_dir}"

  if [[ "${MODE}" == "link" ]]; then
    ln -s "${LOCAL_SKILL_DIR}" "${target_dir}"
  else
    cp -R "${LOCAL_SKILL_DIR}" "${target_dir}"
  fi

  write_config_env "${target_dir}"

  cat <<EOF
Installed memory-transfer skill to ${target_dir}
Install source: local checkout
Install mode: ${MODE}
MEMORY_TRANSFER_SERVER_URL: ${SERVER_URL}
EOF
}

install_from_remote() {
  if [[ "${MODE}" == "link" ]]; then
    echo "--link only works from a local checkout. Use --copy for remote install." >&2
    exit 1
  fi

  if command -v curl >/dev/null 2>&1; then
    DOWNLOAD_CMD=(curl -fsSL)
  elif command -v wget >/dev/null 2>&1; then
    DOWNLOAD_CMD=(wget -qO-)
  else
    echo "curl or wget is required for remote skill install." >&2
    exit 1
  fi

  local archive_url="https://codeload.github.com/${REPO_SLUG}/tar.gz/refs/heads/${REPO_REF}"
  local temp_dir
  temp_dir="$(mktemp -d)"
  trap "rm -rf '${temp_dir}'" EXIT

  "${DOWNLOAD_CMD[@]}" "${archive_url}" | tar -xzf - -C "${temp_dir}"

  local extracted_skill_dir="${temp_dir}/memory-transfer-${REPO_REF}/skills/memory-transfer"
  if [[ ! -d "${extracted_skill_dir}" ]]; then
    echo "Failed to locate skills/memory-transfer in ${REPO_SLUG}@${REPO_REF}" >&2
    exit 1
  fi

  local target_root target_dir
  target_root="$(resolve_skills_dir)"
  target_dir="${target_root}/memory-transfer"

  mkdir -p "${target_root}"
  rm -rf "${target_dir}"
  cp -R "${extracted_skill_dir}" "${target_dir}"
  write_config_env "${target_dir}"

  cat <<EOF
Installed memory-transfer skill to ${target_dir}
Install source: https://github.com/${REPO_SLUG}
Install ref: ${REPO_REF}
Install mode: copy
MEMORY_TRANSFER_SERVER_URL: ${SERVER_URL}
EOF
}

prompt_skills_dir
prompt_server_url

if [[ -d "${LOCAL_SKILL_DIR}" ]]; then
  install_from_local
else
  install_from_remote
fi
