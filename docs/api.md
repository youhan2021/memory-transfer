# API

Base URL example:

```text
http://127.0.0.1:8000
```

## `GET /health`

Returns service health and basic store stats.

Example response:

```json
{
  "status": "ok",
  "service": "memory-transfer-server",
  "active_transfers": 1
}
```

## `POST /transfer/create`

Creates a temporary transfer session from a memory bundle.

Request body:

```json
{
  "bundle": {
    "version": "1.0",
    "source_agent": "source-agent-demo",
    "exported_at": "2026-04-21T00:00:00Z",
    "memories": []
  },
  "ttl_seconds": 600
}
```

Response body:

```json
{
  "transfer_id": "tr_xxx",
  "short_code": "mango-river-27",
  "confirm_phrase": "silver bamboo",
  "expires_at": "2026-04-21T00:10:00Z"
}
```

## `POST /transfer/lookup`

Looks up a transfer session by short code and returns preview only.

Request body:

```json
{
  "short_code": "mango-river-27"
}
```

Response body:

```json
{
  "transfer_id": "tr_xxx",
  "short_code": "mango-river-27",
  "status": "pending",
  "preview": {
    "source_agent": "hermes",
    "exported_at": "2026-04-21T00:00:00Z",
    "expires_at": "2026-04-21T00:10:00Z",
    "memory_count": 15,
    "memory_type_counts": {
      "preference": 12,
      "workflow": 3
    },
    "requires_confirm_phrase": true
  }
}
```

The lookup response does not return full memory content.

## `POST /transfer/confirm-import`

Confirms a transfer with short code plus confirm phrase.

Request body:

```json
{
  "short_code": "mango-river-27",
  "confirm_phrase": "silver bamboo",
  "import_mode": "upsert"
}
```

Response body:

```json
{
  "transfer_id": "tr_xxx",
  "short_code": "mango-river-27",
  "status": "consumed",
  "import_mode": "upsert",
  "consumed_at": "2026-04-21T00:03:00Z",
  "bundle": {
    "version": "1.0",
    "source_agent": "hermes",
    "exported_at": "2026-04-21T00:00:00Z",
    "memories": []
  }
}
```

After `confirm-import` succeeds, the transfer session is consumed and cannot be used again.
