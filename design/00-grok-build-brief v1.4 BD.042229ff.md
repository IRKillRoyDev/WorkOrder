# 00 Grok Build Brief (start here)

> **Rough bookmark.** These files describe software for you (Grok Build) to write. They tell you what the software must do and how it must protect the data. They don't control how you work. If something here is unclear, ask the owner in the chat.
> Revised 2026-10-31: the disk is not encrypted. The app creates the database and encrypts that file. The owner unlocks it with a passphrase. There is no hardware key and no SSH.
> Revised 2026-10-31: v1 is a work order. Issues are chosen from the troubleshooting manual by system. Time to repair uses those steps, the parts manual, and DSI, SMU, and RIP on-hand quantities. Vehicle details come later.

## Who is who
- **You (Grok Build)** write the software, its tests and its docs. You may use a shell to write and test. The owner does not.
- **The owner** is the person you're working with in the chat. He opens the finished WorkOrder app, as himself, on the deployment host he sets (`06` OD-1, OD-2). Real manuals are only ever on that host, never on the machine where you build unless it is that host.

## What the software is (one paragraph)
A Mac desktop application for planners and maintenance. You open a work order, choose the issues found on a limited technical inspection, and the app estimates the time to repair. The issues are systems on the vehicle, such as Engine or Transmission, and each issue is chosen from the troubleshooting manual rather than typed in. The app reads a troubleshooting manual and a parts manual, and it reads on-hand quantities from Demand Supported Items (DSI), SASSY Management Unit (SMU), and Repairable Issue Point (RIP) inventories. It stores what it extracts in a database it creates and encrypts. Vehicle details are a later addition. The manuals are **CUI** (Controlled Unclassified Information), not classified, and the software treats every input as CUI by default.

## How the owner uses it
He opens **WorkOrder**, a Mac application with its own windows (`06` OD-19, closed). He is the only operator. The first time, he picks a normal folder and chooses a passphrase. The app creates the database there and encrypts that file. Later, he types the passphrase on the Unlock screen (`04` S5, `06` OD-21). There is no hardware key, no SSH, and no SSH key. He does not use a terminal, a shell, a browser, Quick Look, or Preview. The windows are desktop widgets, not a web view (`06` OD-20). Pytest calls the same functions those screens call.

## The data rule
You don't need any manual content to write this software, so you never open, list, read or ask for it. Manuals, extracted records, review bundles, the database, keys and the audit log all live in a separate encrypted data location outside the repo (`09`). The software is configured to point at it. Nothing from there is ever committed, pasted into the chat or written into a log. If manual content ever shows up where you can see it (a file in the repo, a paste in the chat, an error message with page text), stop reading it, don't copy or summarize it, and tell the owner in the chat (`04` S12).

When a real-data run goes wrong, the owner gives you error codes, row IDs, counts, page indexes and hashes. That is enough to fix the code.

## Reading order
1. `00` (this file)
2. `09`: where things go (repo layout and data location)
3. `04`: data protections the software must implement
4. `08`: tools and the compromise check
5. `01`: database schema
6. `02`: PDF extraction pipeline
7. `03`: revision tracking
8. `05`: capabilities
9. `10`: acceptance tests for each build step
10. `12`: definition of done
11. `11`: when to tell the owner something in the chat
12. `06`: open decisions, each with the Default to build on

`07-lab-review.md` is background history. Don't build from it. Where it disagrees with these files, these files win.

**If two files disagree:** `00` wins, then `04`, then the file closest to the step at hand. If it's still unclear, ask the owner in the chat.

## Build order (each step ends with its tests in `10`)
0. **Repo setup** (`09`): the folder layout, `.gitignore` (Python template plus the CUI block lines), `pyproject.toml`, a hash-pinned `requirements.lock`, and `docs/compromise-check.md` with a row for every component before you use it (`08`).
1. **Data folder, the app window, and startup checks** (`04`, `09`, `05`): the app reads the data folder from the owner's first-run choice (tests use `WORKORDER_DATA`). It refuses to create or open the database if that folder is missing or inside the repo. It does not require the disk to be encrypted. The database file it creates is encrypted, and the Unlock screen asks for the passphrase. Later steps add their screens to this same app.
2. **Schema** (`01`): nine core tables, one view and the support tables. Every extracted row carries `revision_id`, `source_page`, `change_no`, `marking` and `batch_id`.
3. **Shared preprocessing** (`02` steps 0 to 6): intake checks, per-page text vs. scanned, local Tesseract OCR, split with page labels kept, **capture markings before header strip**, strip, normalize, revision block and per-page change number.
4. **Tech manual parser**, then the **parts manual parser** (`02`).
5. **Cross-parser reconciliation**, which writes `mismatches.csv` (`02`).
6. **CSV output and review bundle** (`02`).
7. **Load confirm step** (`02`, `06` OD-14): the Load screen shows the manifest hash, the highest marking and the counts, and loads only after he confirms.
8. **Encrypted load**, with audit events (`04`).
9. **Revision diffing**: all columns, latest as default, old revisions kept (`03`).
10. **Work order** (`05`): new work order, major defects chosen by system from the troubleshooting steps, other defects as free text, Diagnose / Repair / Replace averages, outcomes and repair parts, mandatory-replacement parts, on-hand quantities from DSI, SMU, and RIP, the time-to-repair estimate, and the defect list. When this passes, tell the owner in the chat. The deferred items in `05` wait until he says so.
11. **Backup, restore and purge** (`04`), each as an action on the Maintain screen.

The owner does every one of these in the app. He is never asked to type a shell command.

**Scope:** one work order with issues chosen from one troubleshooting manual and its parts manual, end to end. The owner picks the pilot manuals and the issues (`06` OD-5) and runs it himself. Vehicle details are not part of this scope.

## Data protections (summary; detail in `04`)
- **Data outside the repo.** Manuals, extracted records and the database never go in the repo. `.gitignore` blocks PDFs, CSVs, database files, disk images and keys, and a test checks that git tracks none of them (`09`, `10`).
- **Encrypted at rest.** The disk is a normal folder. The app creates the database and encrypts that file with SQLCipher 4 (`06` OD-3, OD-21). That is the protection. It is not a classified-data system.
- **Unlock.** The owner chooses a passphrase when the database is created and types it to open the app. The app does not store the passphrase. There is no hardware key, no SSH, and no FIPS module (`04` S5, `06` OD-21).
- **No network.** The software contains no network code and no SSH client or server. A test proves it runs with networking blocked (`04` S3).
- **No AI touches manual content.** The software is deterministic code with no model calls. No LLM or AI tool ever receives manual-derived data.
- **Audit log.** Every decryption and the other events in `04` S7 go to a hash-chained log in the data location. It never contains CUI text.
- **Markings.** Banner and portion markings, distribution statements and export warnings are captured before header strip and carried to every row. Every screen that shows rows repeats the highest marking at the top and the bottom.
- **Desktop app.** Its own windows on the Mac. Not a terminal and not a browser (`06` OD-19, OD-20).
- **Copies.** Intermediates, CSVs, review bundles, backups and logs are as sensitive as the PDFs. They stay in the data location or on encrypted backup drives, never in cloud sync, and batch work areas are crypto-erased after a validated load.
- **Compromise check.** Before you use any tool, library or dependency, check it for known compromise and record the result in `docs/compromise-check.md` (`08`).

## Known risks to watch (`02`)
Duplicate callout numbers across figures. OCR misreads of part numbers. Missing figure references (a parts list split across pages, with the figure number only in a header). Part numbers that don't match across files, handled by normalization rule PNNORM-1 in `02`.
