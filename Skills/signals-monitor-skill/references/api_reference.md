# Signals Monitor — API Reference

## Signal Types
| Signal File | Written By | Read By | Meaning |
|-------------|-----------|---------|---------|
| HEALTH_CHECK_*.md | Cloud | Local | Cloud alive hai |
| CLOUD_DOWN_*.md | Watchdog | Local | Cloud offline |
| APPROVAL_EXPIRED_*.md | Cloud | Local | 24hr approval nahi mila |
| SYNC_CONFLICT_*.md | git_sync.py | Both | Git conflict |
| TASK_FAILED_*.md | Cloud | Local | Task fail hua |

## Folder Structure
- `/Signals/` — Unread signals
- `/Signals/Acknowledged/` — Read signals (archive)

## Scripts
- `signals_writer.py` — Cloud VM pe deploy karo
- `signals_reader.py` — Local PC pe deploy karo
