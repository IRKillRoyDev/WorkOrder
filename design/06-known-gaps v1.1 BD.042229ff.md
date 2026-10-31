# 06 Known Gaps and Open Decisions

> **Rough bookmark, not a finished spec.** It captures what we discussed so the concept is understood. Start at `00`.

## Decisions (owner only)
18 decisions: 16 open with recommended defaults, 2 closed (OD-2, OD-4). Grok Build builds on the recommended default and tells the owner in the chat which default it used. If the owner picks something else, Grok Build changes it. Only Adam closes these, by writing the choice and date on the line.

| ID | Decision | Options | Recommended default | Blocks |
|---|---|---|---|---|
| OD-1 | Operating system | macOS; a Linux distribution in FIPS mode | macOS, the OS of the machine the repo lives on. The deployment host itself is set by the owner under OD-2 | build step 1 |
| OD-2 | CUI on the deployment host | **CLOSED 2026-10-30 by Adam** | Adam's decision: no written basis is required before real manuals load. The tool is not meant to live on a personal computer; the deployment host is not a personal computer, and its host type is set by Adam. The no-transmission and network-block controls (`04` S3, S8) stay as they are. | none (closed) |
| OD-3 | Database engine | SQLite + SQLCipher 4; PostgreSQL + full-disk only | SQLite + SQLCipher 4 | build step 2 |
| OD-4 | FIPS 140-3 module for database crypto | **CLOSED 2026-10-30 by Adam** | Adam's decision: use the industry-standard choice, SQLCipher 4 on the OS FIPS-mode OpenSSL provider. Every security component and dependency is checked for compromise first: Grok Build's CVE lookup before choosing (`00`), and the admin's pre-use compromise check, including an Active CMVP certificate (`04` S11, `10` C0). | none (closed) |
| OD-5 | Pilot manual and symptom | any one engine-system TM + its RPSTL, one symptom | The owner picks one engine system and one symptom; Grok Build never sees the choice's content | owner run |
| OD-6 | Inventory source | CSV export from the shop's supply system; manual entry | CSV export with the columns in `05` | cap 1, 4, 7 |
| OD-7 | Who the software and the build run as | the owner's own macOS account; a separate macOS account; an offline VM | No separate account. Grok Build works as the owner, and the software runs as whoever is unlocking it (`04` S5). A separate account or VM only if the owner chooses one | none |
| OD-8 | Zone-to-figure mapping | owner-kept CSV; parsed from the TM | Software proposes, owner-kept CSV confirmed at the review step | cap 6 |
| OD-9 | "Ten tables" framing | ten core objects (nine tables + one view) plus support tables; strictly ten tables | Ten core objects plus support tables | none |
| OD-10 | Retention for old revisions and the audit log | contract-set period; keep all | Keep all until the contract sets a period | purge of old revisions |
| OD-11 | Text vs. scanned page threshold | 200 characters; other | 200 characters per page, tuned only by the owner from error counts | none |
| OD-12 | Shop hours per day; MAC min/max labor | 8 h/day, min = max = MAC hours; other | 8 h/day; min = max = MAC hours unless the MAC prints a range | cap 7 |
| OD-13 | If a file ever arrives with a classified marking (not expected; manuals are CUI), what should the software do? | stop that file and alert the owner; other | Stop that file and alert the owner | none |
| OD-14 | How the owner approves a batch before real data loads | typed confirm in the software; a cryptographic signature | Typed confirm: the load step shows the manifest sha256, highest marking and counts, and loads only after the owner types the first 8 characters of the sha256. Recorded in `load_batches` and the audit log. No signature (`02`) | build step 7 |
| OD-15 | macOS build of the OD-4 pick | SQLCipher built against the OpenSSL 3 FIPS provider; SQLCipher's commercial FIPS edition | Build OpenSSL 3 with the FIPS provider from a release the OpenSSL project lists as validated, and SQLCipher plus `sqlcipher3` against it (script in `scripts/`). macOS has no OS FIPS mode, and community SQLCipher's `PRAGMA cipher_fips_status` reports 0, so the software instead checks at startup that the OpenSSL `fips` provider is available and refuses to open the database otherwise. The provider's CMVP certificate must be Active (compromise check). Sources: https://docs.openssl.org/master/man7/OSSL_PROVIDER-FIPS/ , https://www.zetetic.net/sqlcipher/sqlcipher-api/ , https://github.com/sqlcipher/sqlcipher/blob/master/src/crypto_openssl.c | build step 1, 2 |
| OD-16 | How each PDF parse is isolated | child process with limits plus a `sandbox-exec` profile; child process with limits only | Child process per PDF with wall-time, page and pixel limits, started under a `sandbox-exec` profile that denies network and allows writes only to that batch's folder. Open because Apple marks `sandbox-exec` deprecated and the profile language is undocumented, though it still works. Sources: https://man.freebsd.org/cgi/man.cgi?manpath=macOS+26.3&query=sandbox-exec&sektion=1 , https://developer.apple.com/forums/thread/661939 | build step 3 |
| OD-17 | OS-level network block | `sandbox-exec` profile denying network for the whole `workorder` process; a per-app outbound firewall rule; no-network code and test only | `workorder` re-starts itself under a `sandbox-exec` profile that denies network, on top of having no network code and a no-network test (`04` S3). Same deprecation caveat as OD-16. Deny by default: NIST SP 800-171r3 03.13.06, https://csrc.nist.gov/pubs/sp/800/171/r3/final | build step 1 |
| OD-18 | Form of the encrypted data location | an APFS (Encrypted) volume; an encrypted disk image (256-bit AES) | An APFS (Encrypted) volume on the deployment host, set via `WORKORDER_DATA`, with FileVault on for the startup disk. An encrypted disk image is the fallback where a volume can't be added. Sources: https://support.apple.com/guide/disk-utility/add-delete-or-erase-apfs-volumes-dskua9e6a110/mac , https://support.apple.com/guide/disk-utility/create-a-disk-image-dskutl11888/mac , https://infosec.ed.ac.uk/how-to-protect/encrypting/encrypted-containers/mac-create-disk-image | build step 1 |

## Deferred design (not built in v1)
- **D1. Deadline flag** (capability 8). Rule is fixed in `05`. Build after 1 to 7 are accepted.
- **D2. Quantity roll-up** for totals at the assembly level (capability 9). Needs an assembly hierarchy above figures; not designed.
- **D3. Shop-floor feedback loop** for confidence scoring (capability 10). Needs `diagnostic_outcomes` data, a scoring rule, and who may write outcomes (audited).
- **D4. Diagram image reading.** v1 reads parts-list tables only (`02`).

## Closed here
- OD-2 and OD-4: closed 2026-10-30 by Adam (rows above). Only their cross-references to removed sections were updated; the decisions are unchanged.
- Part-number normalization across files: now rule PNNORM-1 in `02`, versioned, raw value kept.
