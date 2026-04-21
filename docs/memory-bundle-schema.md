# Memory Bundle Schema

Minimum bundle fields:

- `version`
- `source_agent`
- `exported_at`
- `memories`

Each memory item includes:

- `id`
- `type`
- `title`
- `content`
- `tags`
- `transferable`
- `sensitivity`

Recommended stable export types:

- `preference`
- `profile`
- `project_context`
- `workflow`
- `tool_preference`

Usually excluded by default:

- `temporary`
- local filesystem paths
- device-specific settings
- cache-like material
