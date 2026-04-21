#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
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

for arg in "$@"; do
  case "$arg" in
    --link)
      MODE="link"
      ;;
    --copy)
      MODE="copy"
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 1
      ;;
  esac
done

TARGET_ROOT="$(resolve_skills_dir)"
TARGET_DIR="${TARGET_ROOT}/memory-transfer"

mkdir -p "${TARGET_ROOT}"
rm -rf "${TARGET_DIR}"

if [[ "${MODE}" == "link" ]]; then
  ln -s "${SKILL_DIR}" "${TARGET_DIR}"
else
  cp -R "${SKILL_DIR}" "${TARGET_DIR}"
fi

echo "Installed memory-transfer skill to ${TARGET_DIR}"
