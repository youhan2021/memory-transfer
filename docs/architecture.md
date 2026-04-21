# Architecture

`memory-transfer` is a small monorepo with two main runtime pieces:

- `backend/`: temporary relay service for bundles
- `skills/memory-transfer/`: OpenClaw-style skill for export, lookup, confirm-import, and local import

## Design Principles

- Low friction over complete abstraction
- Transfer over sync
- Temporary relay over persistent storage
- File-based demo over production dependencies
- Preview before import

## Backend Responsibilities

- Accept a validated memory bundle
- Generate `transfer_id`, `short_code`, and `confirm_phrase`
- Store bundle in memory with optional file snapshot persistence
- Enforce TTL
- Support preview lookup and one-time confirm-import behavior

## Skill Responsibilities

- Read local or mock memory source data
- Generate a transferable bundle
- Show source-side short code plus confirm phrase
- Preview the bundle before import
- Confirm import with short code plus confirm phrase
- Apply import modes: `append`, `replace`, `upsert`

## Shared Assets

- `schemas/` defines wire contracts
- `examples/` provides a sample bundle
- `shared/` documents memory types and conflict policy
