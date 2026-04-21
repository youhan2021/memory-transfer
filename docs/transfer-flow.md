# Transfer Flow

## Source Side

1. Read local memory source data
2. Build a bundle
3. Upload the bundle to the relay backend
4. Receive `short_code`, `confirm_phrase`, and `expires_at`
5. Share the short code and confirm phrase with the target user through conversation

## Target Side

1. Enter the short code
2. Call lookup and show preview only
3. Ask the user for the confirm phrase
4. Call confirm-import with `short_code + confirm_phrase`
5. Import with `append`, `replace`, or `upsert`
6. Mark the transfer consumed

## Why This Is Not Sync

- No long-lived session
- No account identity
- No incremental state replication
- No background updates
