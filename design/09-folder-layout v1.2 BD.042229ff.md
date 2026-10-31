# 09 Repo Layout and Data Location

> **Rough bookmark.** This replaces the old OS-users-and-paths table. There are no separate OS accounts and no system paths. The data lives in one encrypted location outside the repo.

## The repo (everything you write)
Paths are relative to the repo root.
```
WorkOrder/
  README.md
  .gitignore            Python template plus the CUI block lines below
  pyproject.toml
  requirements.in       direct dependencies
  requirements.lock     every dependency pinned with its sha256 hash
  src/workorder/        the software
  tests/                pytest suites (`10`)
  docs/design/          these design files
  docs/compromise-check.md   one row per component (`08`)
  docs/data-setup.md    how the owner sets up the data location and backups (`04`)
  scripts/              build helpers, for example the SQLCipher build (`08`)
```
The Python virtual environment lives at `.venv/` in the repo root. The Python `.gitignore` template already ignores it.

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
One encrypted APFS volume or encrypted disk image that the owner creates and mounts (`04` S4, `06` OD-18), for example `/Volumes/WorkOrderData`. The software reads its path from the environment variable `WORKORDER_DATA`. It refuses to start if the variable is missing, if the path is inside the repo, or if the volume isn't encrypted. It must not be under `~/Desktop` or `~/Documents`, which iCloud can sync.
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
