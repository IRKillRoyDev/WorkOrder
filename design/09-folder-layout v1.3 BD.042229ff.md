# 09 Repo Layout and Data Location

> **Rough bookmark.** This replaces the old OS-users-and-paths table. There are no separate OS accounts and no system paths. The data lives in one encrypted location outside the repo.
> Revised 2026-10-30: the owner opens `WorkOrder.app`. He does not start the software from a shell.

## The repo (everything you write)
Paths are relative to the repo root.
```
WorkOrder/
  README.md
  .gitignore            Python template plus the CUI block lines below
  pyproject.toml
  requirements.in       direct dependencies
  requirements.lock     every dependency pinned with its sha256 hash
  src/workorder/        the software, including `ui/` for the Mac windows (`06` OD-20)
  tests/                pytest suites (`10`). They call the same functions the screens call
  docs/design/          these design files
  docs/compromise-check.md   one row per component (`08`)
  docs/data-setup.md    how the owner sets up the data location and backups (`04`), as Disk Utility, System Settings, and the app's screens
  scripts/              build helpers: the SQLCipher build, and the script that builds `WorkOrder.app` (`08`)
```
The Python virtual environment lives at `.venv/` in the repo root. The Python `.gitignore` template already ignores it. Also ignore `WorkOrder.app/` and other build output. Do not put those lines in the CUI block below.

## The application the owner opens
`scripts/` builds `WorkOrder.app`. The owner opens that app on the deployment host. Tests import `src/workorder` and do not need the `.app`. The built app is not committed.

## .gitignore
Start from GitHub's Python template (the owner's pick), then add this block at the end:
```
# CUI: manual content, extracted data, databases and keys never go in the repo
*.pdf
*.PDF
*.csv
*.CSV
*.db
*.db-journal
*.db-wal
*.db-shm
*.sqlite
*.sqlite3
*.dmg
*.sparsebundle
*.sparseimage
*.key
*.pem
*.wrapped
audit.jsonl
manuals/
quarantine/
batches/
backups/
data/
keys/
```
Tests never need any of these committed. A test (`10` C1) fails if `git ls-files` lists any file matching these patterns.

## The data location (outside the repo)
One encrypted APFS volume or encrypted disk image that the owner creates and mounts (`04` S4, `06` OD-18), for example `/Volumes/WorkOrderData`. On first launch the app asks him to choose that volume and saves only the path in `~/Library/Application Support/WorkOrder/config.json`. That file holds the path and nothing else. It is outside the repo, it is not CUI text, and it must not be synced. Later launches read it. Tests set `WORKORDER_DATA` instead of the config file, and the env var wins when it is set. The app refuses to open the database if the path is missing, inside the repo, or on a volume that isn't encrypted. The volume must not be under `~/Desktop` or `~/Documents`, which iCloud can sync.
```
<data location>/
  manuals/          PDFs the owner drops in
  quarantine/       rejected files, with an error code
  batches/<batch>/  one encrypted disk image per batch: pages, markings, run log, review bundle
  workorder.db      the SQLCipher database
  keys/             the wrapped database key and wrapped batch-image passwords (never plain)
  audit.jsonl       the hash-chained audit log
  tmp/              temp files for the software and the PDF parser
```
The software creates these folders on first run. You never open them.
