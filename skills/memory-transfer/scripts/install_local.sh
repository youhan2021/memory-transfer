#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
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

while [[ $# -gt 0 ]]; do
  case "$1" in
    --link)
      MODE="link"
      shift
      ;;
    --copy)
      MODE="copy"
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
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "${SKILLS_DIR_INPUT}" ]]; then
  if [[ -t 0 ]]; then
    printf 'Skill install directory [%s]: ' "${HOME}/.openclaw/skills"
    read -r input_dir
    SKILLS_DIR_INPUT="${input_dir:-${HOME}/.openclaw/skills}"
  else
    SKILLS_DIR_INPUT="${HOME}/.openclaw/skills"
  fi
fi

if [[ -z "${SERVER_URL}" ]]; then
  if [[ -t 0 ]]; then
    printf 'MEMORY_TRANSFER_SERVER_URL [%s]: ' "${DEFAULT_SERVER_URL}"
    read -r input_url
    SERVER_URL="${input_url:-${DEFAULT_SERVER_URL}}"
  else
    SERVER_URL="${DEFAULT_SERVER_URL}"
  fi
fi

TARGET_ROOT="$(resolve_skills_dir)"
TARGET_DIR="${TARGET_ROOT}/memory-transfer"

mkdir -p "${TARGET_ROOT}"
rm -rf "${TARGET_DIR}"

if [[ "${MODE}" == "link" ]]; then
  ln -s "${SKILL_DIR}" "${TARGET_DIR}"
else
  cp -R "${SKILL_DIR}" "${TARGET_DIR}"
fi

cat > "${TARGET_DIR}/config.env" <<EOF
MEMORY_TRANSFER_SERVER_URL=${SERVER_URL}
EOF

echo "Installed memory-transfer skill to ${TARGET_DIR}"
echo "Skill install directory: ${TARGET_ROOT}"
echo "MEMORY_TRANSFER_SERVER_URL: ${SERVER_URL}"
