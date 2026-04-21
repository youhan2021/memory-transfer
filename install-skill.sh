#!/usr/bin/env bash
set -euo pipefail

REPO_SLUG="${MEMORY_TRANSFER_REPO:-youhan2021/memory-transfer}"
REPO_REF="${MEMORY_TRANSFER_REF:-main}"
MODE="copy"

resolve_skills_dir() {
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
  ./install-skill.sh --ref <git-ref>
  ./install-skill.sh --repo <owner/repo>

Environment:
  MEMORY_TRANSFER_REPO   Override GitHub repo, default: ${REPO_SLUG}
  MEMORY_TRANSFER_REF    Override git ref, default: ${REPO_REF}

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
TARGET_ROOT="$(resolve_skills_dir)"
TARGET_DIR="${TARGET_ROOT}/memory-transfer"

install_from_local() {
  mkdir -p "${TARGET_ROOT}"
  rm -rf "${TARGET_DIR}"

  if [[ "${MODE}" == "link" ]]; then
    ln -s "${LOCAL_SKILL_DIR}" "${TARGET_DIR}"
  else
    cp -R "${LOCAL_SKILL_DIR}" "${TARGET_DIR}"
  fi

  cat <<EOF
Installed memory-transfer skill to ${TARGET_DIR}
Install source: local checkout
Install mode: ${MODE}
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
  trap 'rm -rf "${temp_dir}"' EXIT

  "${DOWNLOAD_CMD[@]}" "${archive_url}" | tar -xzf - -C "${temp_dir}"

  local extracted_skill_dir="${temp_dir}/memory-transfer-${REPO_REF}/skills/memory-transfer"
  if [[ ! -d "${extracted_skill_dir}" ]]; then
    echo "Failed to locate skills/memory-transfer in ${REPO_SLUG}@${REPO_REF}" >&2
    exit 1
  fi

  mkdir -p "${TARGET_ROOT}"
  rm -rf "${TARGET_DIR}"
  cp -R "${extracted_skill_dir}" "${TARGET_DIR}"

  cat <<EOF
Installed memory-transfer skill to ${TARGET_DIR}
Install source: https://github.com/${REPO_SLUG}
Install ref: ${REPO_REF}
Install mode: copy
EOF
}

if [[ -d "${LOCAL_SKILL_DIR}" ]]; then
  install_from_local
else
  install_from_remote
fi
