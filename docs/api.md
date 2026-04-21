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

Creates a temporary transfer from a memory bundle.

Request body:

```json
{
  "bundle": {
    "version": "1.0",
    "source_agent": "source-agent-demo",
    "exported_at": "2026-04-21T00:00:00Z",
    "memories": []
  },
  "ttl_seconds": 3600,
  "consume_once": true
}
```

Response body:

```json
{
  "transfer_id": "tr_xxx",
  "expires_at": "2026-04-21T01:00:00Z",
  "short_code": "ABC123",
  "qr_payload": "memory-transfer://fetch?transfer_id=tr_xxx&code=ABC123",
  "consume_once": true
}
```

## `GET /transfer/{transfer_id}`

Query parameters:

- `preview=true|false`

Preview mode returns bundle metadata and lightweight item summaries. Full mode returns the actual bundle.

## `POST /transfer/{transfer_id}/consume`

Marks a transfer as consumed. One-time transfers will not be fetchable after consumption.
