# Conflict Policy

The MVP supports three import modes:

- `append`
- `replace`
- `upsert`

Conflict identity is based on `memory.id`.

Practical defaults:

- `append` for intentionally additive memory stores
- `replace` for clean overwrite workflows
- `upsert` for most day-to-day transfer cases
