# Conflict Rules

Default conflict behavior:

- identity key is `memory.id`
- `append` keeps duplicates if the caller wants raw accumulation
- `replace` discards old target entries
- `upsert` overwrites matching IDs and preserves unrelated existing memories

This MVP does not implement field-level merge policies.
