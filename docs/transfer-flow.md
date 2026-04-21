# Transfer Flow

## Source Side

1. Read local memory source data
2. Filter memories by `transferable=true`
3. Exclude temporary or device-specific records
4. Build a bundle
5. Upload bundle to relay backend
6. Receive `transfer_id`, short code, and QR payload

## Target Side

1. Fetch preview with `transfer_id`
2. Inspect counts and memory summaries
3. Import with `append`, `replace`, or `upsert`
4. Optionally consume the transfer

## Why This Is Not Sync

- No long-lived session
- No account identity
- No incremental state replication
- No background updates
