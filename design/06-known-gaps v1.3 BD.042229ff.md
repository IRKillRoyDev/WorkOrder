# 06 Known Gaps and Open Decisions

> **Rough bookmark, not a finished spec.** It captures what we discussed so the concept is understood. Start at `00`.
> Revised 2026-10-31: OD-21 is the at-rest rule. OD-4, OD-15, and OD-18 are superseded. Do not build an encrypted volume, a hardware key, SSH, or a FIPS module.

## Decisions (owner only)
21 decisions: 15 open with recommended defaults, 6 closed (OD-2, OD-4, OD-15, OD-18, OD-19, OD-21). Grok Build builds on the recommended default and tells the owner in the chat which default it used. If the owner picks something else, Grok Build changes it. Only Adam closes these, by writing the choice and date on the line. OD-4, OD-15, and OD-18 stay in the table so the old choice is visible, and OD-21 overrides them.

| ID | Decision | Options | Recommended default | Blocks |
|---|---|---|---|---|
| OD-1 | Operating system | macOS; a Linux distribution | macOS, the OS of the machine the repo lives on. The deployment host itself is set by the owner under OD-2 | build step 1 |
| OD-2 | CUI on the deployment host | **CLOSED 2026-10-30 by Adam** | Adam's decision: no written basis is required before real manuals load. The tool is not meant to live on a personal computer; the deployment host is not a personal computer, and its host type is set by Adam. The app still has no network code (`04` S3) and does not sync the data folder (`04` S8). | none (closed) |
| OD-3 | Database engine | SQLite + SQLCipher 4; PostgreSQL + full-disk only | SQLite + SQLCipher 4 | build step 2 |
| OD-4 | FIPS 140-3 module for database crypto | **SUPERSEDED 2026-10-31 by OD-21** | Do not build this. An earlier close picked SQLCipher on a FIPS OpenSSL provider. Adam replaced that on 2026-10-31: normal SQLCipher AES-256 is enough. No FIPS module and no CMVP certificate. | none (superseded) |
| OD-5 | Pilot manuals and issues | any one troubleshooting manual plus its parts manual, and the issues the owner selects | The owner picks the manuals and the work-order issues. Grok Build never sees the choice's content. Vehicle details are out of scope (`05`) | owner run |
| OD-6 | Inventory source | DSI, SMU, and RIP lists; one combined list | Three lists: DSI, SMU, and RIP. Each row is a part number and an on-hand quantity. No lead time in the file (`05`) | work order |
| OD-7 | Who the software and the build run as | the owner's own macOS account; a separate macOS account; an offline VM | No separate account. Grok Build works as the owner, and the software runs as the person who typed the passphrase (`04` S5). A separate account or VM only if the owner chooses one | none |
| OD-8 | Zone-to-figure mapping | owner-kept CSV; parsed from the TM | Software proposes, owner-kept CSV confirmed at the review step | cap 6 |
| OD-9 | "Ten tables" framing | ten core objects (nine tables + one view) plus support tables; strictly ten tables | Ten core objects plus support tables | none |
| OD-10 | Retention for old revisions and the audit log | contract-set period; keep all | Keep all until the contract sets a period | purge of old revisions |
| OD-11 | Text vs. scanned page threshold | 200 characters; other | 200 characters per page, tuned only by the owner from error counts | none |
| OD-12 | Where the repair time comes from | per-task hours from the manual; system averages the planner enters | Preferences, by system: the whole system name, then average days to Diagnose, to Repair, and to Replace. Each action has a checkbox. Unchecked leaves that action out of the time. Plus one average lead time in days when a part is not on hand. No per-task times and no hard-coded stand-in (`05`) | work order |
| OD-13 | If a file ever arrives with a classified marking (not expected; manuals are CUI), what should the software do? | stop that file and alert the owner; other | Stop that file and alert the owner | none |
| OD-14 | How the owner approves a batch before real data loads | typed confirm in the software; a cryptographic signature | Typed confirm on the Load screen: it shows the manifest sha256, highest marking and counts, and loads only after the owner types the first 8 characters of the sha256. Recorded in `load_batches` and the audit log. No signature (`02`, `05`) | build step 7 |
| OD-15 | macOS build of the OD-4 pick | **SUPERSEDED 2026-10-31 by OD-21** | Do not build a FIPS OpenSSL or a commercial FIPS SQLCipher. Use a normal SQLCipher 4 build and the `sqlcipher3` binding (`08`). | none (superseded) |
| OD-16 | How each PDF parse is isolated | child process with limits plus a `sandbox-exec` profile; child process with limits only | Child process per PDF with wall-time, page and pixel limits. No `sandbox-exec` profile. The child gets no network and is not given the database passphrase (`02`). | build step 3 |
| OD-17 | OS-level network block | `sandbox-exec` profile denying network for the whole WorkOrder app; a per-app outbound firewall rule; no-network code and test only | No network code, and a test that fails if the app tries to connect (`04` S3). No `sandbox-exec`. No SSH client and no SSH server. | build step 1 |
| OD-18 | Form of the data location | **SUPERSEDED 2026-10-31 by OD-21** | A normal folder the owner picks. The disk is not encrypted. Do not require FileVault, an APFS encrypted volume, or an encrypted disk image. | none (superseded) |
| OD-19 | How the owner uses the software | **CLOSED 2026-10-30 by Adam** | Adam's decision: a Mac desktop app with its own windows. Not a terminal and not a browser. He is the only operator. v1 is the work order in `05`. | none (closed) |
| OD-20 | Window toolkit | PySide6 (Qt widgets, macOS style); PyObjC/AppKit | PySide6, using the macOS style. No web view and no QtNetwork import. The app is not a browser. PySide6 is LGPL and is used as a shared library. AppKit is the alternative if PySide6 fails the compromise check or Adam prefers system widgets. | build step 1 |
| OD-21 | What is encrypted, and how it unlocks | **CLOSED 2026-10-31 by Adam** | Adam's decision: the volume is not encrypted. The app creates the database and encrypts that file. He sets a passphrase and types it to unlock. This is at-rest protection for CUI, not a secret or top-secret system. No hardware key. No SSH. No FIPS module. No split recovery. | none (closed) |

## Deferred design (not built in v1)
- **D1. Deadline flag** (capability 8). Rule is fixed in `05`. Build after 1 to 7 are accepted.
- **D2. Quantity roll-up** for totals at the assembly level (capability 9). Needs an assembly hierarchy above figures; not designed.
- **D3. Shop-floor feedback loop** for confidence scoring (capability 10). Needs `diagnostic_outcomes` data, a scoring rule, and who may write outcomes (audited).
- **D4. Diagram image reading.** v1 reads parts-list tables only (`02`).

## Closed here
- OD-2: closed 2026-10-30 by Adam (row above).
- OD-4 and OD-15: superseded 2026-10-31 by OD-21. Do not build a FIPS module.
- OD-18: superseded 2026-10-31 by OD-21. The data folder is a normal folder.
- OD-19: closed 2026-10-30 by Adam in chat. The software is a Mac desktop app. He is the only operator. The terminal tool is not built.
- OD-21: closed 2026-10-31 by Adam in chat. Encrypt the database file. Unlock with a passphrase. No hardware key and no SSH.
- Part-number normalization across files: now rule PNNORM-1 in `02`, versioned, raw value kept.
