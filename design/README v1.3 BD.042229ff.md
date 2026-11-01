# Maintenance Estimation System: Design Handoff (2026-10-30)

> **Rough bookmarks**, not finished products. These files describe the software for Grok Build to write. They don't control how Grok Build works. Grok Build starts at `00` and follows its reading order.
> Revised 2026-10-31: the app encrypts the database it creates. The owner unlocks it with a passphrase. The disk is not encrypted. There is no hardware key and no SSH.

This system ingests technical manuals and parts manuals (PDFs), extracts structured data, and builds an encrypted database for maintenance planning, parts availability checks and time-to-repair estimates on military equipment. The manuals are **CUI**. Grok Build writes the software and never needs or sees real manual content. The owner runs the finished software on real manuals, with all data kept in an encrypted location outside the repo.

## Current files
Use these copies. The older same-numbered files in this folder are earlier versions.
| File | What it covers |
|---|---|
| `00-grok-build-brief v1.4 BD.042229ff.md` | **Start here.** Who is who, the Mac app, the passphrase, the data rule, reading order, tie-breaker, concept, build order, data protections summary |
| `01-database-schema v1.0 BD.042229ff.md` | Nine core tables + one view (the "ten"), support tables, keys and types |
| `02-pdf-extraction-pipeline v1.2 BD.042229ff.md` | Intake, preprocessing, marking capture, the two parsers, reconciliation, review bundle, the load confirm screen |
| `03-revision-tracking v1.0 BD.042229ff.md` | Revision order from the owner's publication index, change pages, full-column diffs, latest by default, supersession |
| `04-security-encryption v1.3 BD.042229ff.md` | Data protections: data folder outside the repo, the encrypted database file, passphrase unlock, no network, markings, audit log, copies, backups, purge, the compromise check, spill procedure |
| `05-capability-map v1.4 BD.042229ff.md` | Screens, inputs, the ten capabilities and their rules; build 1 to 7 |
| `06-known-gaps v1.3 BD.042229ff.md` | Decisions (owner only): 21 total, 15 open with recommended defaults, 6 closed or superseded (OD-2, OD-4, OD-15, OD-18, OD-19, OD-21). OD-21 wins on encryption |
| `07-lab-review.md` | Lab's review. Background history only; don't build from it. Where it disagrees with the files above, they win |
| `08-tools-and-offline-bundle v1.4 BD.042229ff.md` | Tools, including normal SQLCipher and the desktop window toolkit, the hash-pinned install and the compromise check |
| `09-folder-layout v1.4 BD.042229ff.md` | The repo layout, `WorkOrder.app`, the `.gitignore` CUI block, and the normal data folder outside the repo |
| `10-acceptance-checks v1.4 BD.042229ff.md` | The tests for every build step, with expected results. Owner rows are actions in the app |
| `11-hard-stops v1.1 BD.042229ff.md` | When to tell the owner in the chat (replaces the old hard stops) |
| `12-definition-of-done v1.4 BD.042229ff.md` | When v1 is done |

## How they connect
- 00 is the entry point. 09 says where things go. 04 says how the data is protected.
- 02 produces the CSVs that load into the tables in 01. 03 supplies `manual_revisions` and the per-row stamps.
- 08 lists the tools and the compromise check. 05 queries the 01 tables. 10 tests each step. 12 says when v1 is done.
- 11 lists the moments to tell the owner something in the chat; he says when to continue.
- 06 collects every decision: 21 total, 15 open with recommended defaults, 6 closed or superseded (OD-2, OD-4, OD-15, OD-18, OD-19, OD-21). OD-19 is the Mac desktop app. OD-21 is the encrypted database and the passphrase. OD-20 is the window toolkit.
- Every tool, library and dependency is checked for known compromise before it is used, with the result recorded in `docs/compromise-check.md` in the repo (`04` S11, `08`, `10` C0). Real manuals load only after the owner confirms each batch in the software (`02`, `06` OD-14).
