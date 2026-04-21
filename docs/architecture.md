# Architecture

`memory-transfer` is a small monorepo with two main runtime pieces:

- `backend/`: temporary relay service for bundles
- `skills/memory-transfer/`: OpenClaw-style skill for export, preview, QR generation, and import

## Design Principles

- Low friction over complete abstraction
- Transfer over sync
- Temporary relay over persistent storage
- File-based demo over production dependencies
- Preview before import

## Backend Responsibilities

- Accept a validated memory bundle
- Generate `transfer_id`, `short_code`, and QR payload
- Store bundle in memory with optional file snapshot persistence
- Enforce TTL
- Support one-time consume behavior

## Skill Responsibilities

- Read local or mock memory source data
- Filter exportable memories
- Generate a transferable bundle
- Preview the bundle before import
- Apply import modes: `append`, `replace`, `upsert`

## Shared Assets

- `schemas/` defines wire contracts
- `examples/` provides a sample bundle
- `shared/` documents memory types and conflict policy
