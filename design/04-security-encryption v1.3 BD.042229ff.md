# 04 Data Protection and Encryption (CUI)

> **Rough bookmark, not a finished spec.** Start at `00`. Everything below is something **the software** must do, or a setup step the owner follows (you write those steps into `docs/data-setup.md`). You never need manual content for any of it. Sources are at the end; anything not fetched and confirmed is marked unverified.
> Revised 2026-10-31: protect the database file at rest. The disk is not encrypted. Unlock is a passphrase. There is no hardware key, no SSH, and no FIPS module (`06` OD-21).

The source manuals are **CUI** (Controlled Unclassified Information), not classified, and not secret or top secret. The protection matches that: an encrypted database file, and a passphrase to open it.

## S1. Data stays out of the repo and out of AI tools
- Manuals, extracted records, review bundles, the database and the audit log live only in the data folder (`09`), never in the repo. `.gitignore` blocks them and a test checks git tracks none of them (`10` C1).
- Real-data problems come back to you only as error codes, row IDs, counts, page indexes and hashes. Nobody pastes manual text, page images or CSV cells into Grok Build or any AI tool.
- "No AI touches manual content" means the software is deterministic code with no model calls.

## S2. Deployment host and export control
- `06` OD-2 is closed by Adam. The deployment host is not a personal computer; the host type is set by Adam. The app still has no network code (S3), does not sync the data folder to the cloud (S8), and does not send manual content to an AI tool (S1).
- Military maintenance manuals are generally ITAR technical data ("information ... required for the ... operation, repair, testing, maintenance": 22 CFR 120.33(a)(1)). So: only U.S. persons with a need to know use the software; content never goes to any cloud service, AI model or foreign-hosted tool; the export warning is captured and carried (S6). DoDI 5230.24 distribution statements are captured as text (that rule itself is unverified here).

## S3. Network
- The software contains no network code: no sockets, HTTP clients, remote calls, SSH client, or SSH server, and no dependency that phones home. A test runs the pipeline and the capabilities with networking blocked and fails on any connection attempt (`10` C1).
- There is no sandbox profile and no SSH login. The PDF parser is a child process with time and size limits (`02`, `06` OD-16).

## S4. Storage and crypto
- **Data folder:** a normal folder the owner chooses (`09`, `06` OD-18, OD-21). The disk is not encrypted, and the app does not check FileVault or refuse to run because the volume is unencrypted. On first launch he picks the folder. The app saves only that path, outside the repo. Later launches read it. Tests set `WORKORDER_DATA` instead. The app refuses the path when it is missing, inside the repo, or under `~/Desktop`, `~/Documents`, or another cloud-sync folder.
- **Database:** the app creates `workorder.db` in that folder and encrypts the file with SQLCipher 4 (`06` OD-3, OD-21). AES-256. This is ordinary at-rest protection for CUI, not a secret or top-secret system. No FIPS module is required. OD-4 and OD-15 are superseded.
- **What stays unencrypted:** the PDFs, the review files, and the batch folders sit in that same folder in the clear while he is working. After a validated load, the app deletes the batch folder (S10). The database file is what stays encrypted.

## S5. Unlock
- **Who uses it:** the owner only (`06` OD-19).
- **Passphrase:** when the database is created, he chooses a passphrase and types it a second time to confirm. The app does not write it down, does not put it in the config file, and does not put it in the audit log. SQLCipher derives the key from it.
- **Later launches:** the Unlock screen asks for that passphrase. The right one opens the database. A wrong one does not, and the screen says the passphrase was not accepted. He can try again. There is no lockout counter.
- **Not used:** no hardware key, no FIDO2 token, no PIN pad, no SSH key, no SSH login, no wrapped key file, no second person, and no split recovery.
- **Forgotten passphrase:** it cannot be reset. A backup copy of `workorder.db` opens only with the same passphrase.
- **Idle:** after 15 minutes with no input, the app closes the database and shows the Unlock screen again.
- **Inside the database:** one passphrase opens the whole file. Queries use read-only connections. Writes go through the load step. Per-table secrecy is not needed.

## S6. Markings (captured before strip, carried everywhere)
- Captured in `02` step 3: banner, portion markings, designation indicator, CUI categories, distribution statement, export warning (32 CFR 2002.20(b), 2002.20(g); DoDI 5200.48 3.4.a, 3.4.f).
- Stored on every row (`marking`) and on `manual_revisions`.
- **Outputs:** every CSV has a `marking` column and every review bundle carries `MARKING.txt`. Every window that shows rows has a banner at the top and the bottom with the highest marking of those rows, plus the distribution statement and export warning. Reports keep the designation indicator. Unknown marking = treated as CUI. A file with a marking above CUI: see `06` OD-13.

## S7. The audit log
- `audit.jsonl` in the data location, written only by the software, opened in append mode. Each line carries `prev_hash` (SHA-256 of the previous line), so any edit or deletion breaks the chain (03.03.08).
- Each line: UTC timestamp, macOS user, event, object IDs and hashes, result, `prev_hash`. **No CUI**: no manual text, part descriptions, thresholds or query parameters; IDs, counts and hashes only (03.03.02).
- **Events:** unlock success and failure (never the passphrase), DB open and close, capability query (capability number and row count), pipeline start and finish per file, intake reject, load confirm (accepted or refused), load, override applied, backup, restore, purge, chain-check result.
- The Audit screen can check the chain and show the head hash (`05`). Retention: `06` OD-10.

## S8. Copies and leak paths (everything derived is CUI)
- Intermediates, CSVs, review bundles, mismatch files, diffs, logs and backups are as sensitive as the source PDFs. They live only in the data folder. Backups are copies of the already-encrypted database file (S9).
- The software points its temp directory at `tmp/` in the data folder, and the parser child process too. It turns off core dumps for itself and its children (core file size limit 0).
- The data folder is never under `~/Desktop`, `~/Documents`, or any iCloud, Dropbox, or other sync folder. The app refuses those paths. It does not require Spotlight or Time Machine exclusions, and it does not require an encrypted disk.
- The app takes query inputs in its own fields. File picks stay inside the data location. It has no command-line interface, so inputs never land in a shell history.
- Review uses the app's Review screen only (`05`, `08`). No Quick Look, Preview, office suite, browser, web view, or cloud preview opens CUI.
- The app does not print, share, or hand a PDF to another program. Copy places only an explicitly selected part number (`part_number_norm`) on the pasteboard. Lock and quit clear that copy. `docs/data-setup.md` tells the owner to turn Universal Clipboard off.
- No `.bak` copies or ad-hoc exports. The only copies are the backups in S9.

## S9. Backups
- A backup is a copy of `workorder.db` plus `audit.jsonl`, written to a folder the owner chooses in the app. The database copy is already encrypted. The same passphrase opens it. The backup folder is not required to be an encrypted drive. It must not be a cloud-sync folder.
- Backup and restore are audited. Restore replaces the open database only after he confirms on the Maintain screen, and the copy must open with the passphrase he just typed.

## S10. Purge
- Each batch's work area is an ordinary folder, `batches/<batch>/`. After a validated load, purge deletes that folder. Purge is audited with the batch id.
- Old revisions in the database are kept until the retention period in `06` OD-10.

## S11. Supply chain and the compromise check
- Every Python dependency is pinned with its sha256 in `requirements.lock` and installed with `pip install --require-hashes -r requirements.lock`. Native tools (Tesseract, SQLCipher) are pinned to exact versions in `docs/compromise-check.md`.
- **Compromise check (required).** Before any tool, library or dependency is used, check that exact version for known compromise, and check again whenever a dependency is added or changed and before the first real-data run. You (Grok Build) do the lookups; the owner can re-run them. Public data only:
  1. NVD: no unpatched CVE affects the version (none known-exploited, none critical or high).
  2. CISA Known Exploited Vulnerabilities catalog: the component isn't listed, or the version has the fix.
  3. Vendor or project security advisories (OpenSSL, SQLCipher, Python, Tesseract, each library): none open against the version.
  4. Supply-chain incidents (malicious release, compromised maintainer or signing key, tampered package or mirror): none reported for the component or its source.
  5. Downloaded files match their published hash or upstream signature where the project provides one. A FIPS certificate is not required (`06` OD-21).
- **Record:** one row per component in `docs/compromise-check.md`: component, version, sources checked (URL and UTC date), findings (CVE IDs with severity, CISA catalog status, advisory IDs, incident reports, or "none found"), result PASS or FAIL. A FAIL means pick a patched version or an alternative and check that one; if none is clean, tell the owner in the chat (`11`). Do not fail a row for a missing FIPS certificate.
- The PDF parser runs in a separate child process with limits (`02`, `06` OD-16), because a malformed PDF is an attack surface.

## S12. Spill and incident procedure
**Triggers:** CUI found outside the data folder (in the repo, in a chat, in a log); any manual content reaching Grok Build, an AI tool or the cloud; a lost or stolen copy of the database; an audit chain break; a file with a marking above CUI.
**Steps:**
1. Stop the software and disconnect the network.
2. Don't delete anything yet; preserve the evidence.
3. Write down time (local and UTC), what, where, and who.
4. The owner is told at once.
5. The owner reports to the contract's CUI authority or contracting officer within the contract's deadline (DFARS 252.204-7012 sets 72 hours: **unverified**) (03.06.02; DoDI 5200.48 3.9.e).
6. Sanitize only as that authority directs (S10).
7. If the passphrase may have been exposed, the owner sets a new one and the app rekeys the database (S5).
8. Write a short post-incident note: IDs and hashes, no CUI.

## Sources
FileVault, encrypted APFS volumes, FIPS 140-3, and CMVP certificates are not requirements (`06` OD-21). Links about them are history from an earlier draft. Do not build from those links.

Verified by fetch during the Lab review:
- NIST SP 800-171 Rev 3, https://csrc.nist.gov/pubs/sp/800/171/r3/final (controls cited above)
- 32 CFR Part 2002, https://www.ecfr.gov/current/title-32/subtitle-B/chapter-XX/part-2002
- DoDI 5200.48, https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/520048p.PDF
- FIPS 140-3, https://csrc.nist.gov/pubs/fips/140-3/final
- NIST SP 800-88 Rev 2, https://csrc.nist.gov/pubs/sp/800/88/r2/final
- 22 CFR 120.33(a)(1), via eCFR

macOS data location (checked 2026-10-30):
- Apple, Disk Utility: add an APFS (Encrypted) volume, https://support.apple.com/guide/disk-utility/add-delete-or-erase-apfs-volumes-dskua9e6a110/mac
- Apple, Disk Utility: file system formats, APFS (Encrypted), https://support.apple.com/guide/disk-utility/file-system-formats-dsku19ed921c/mac
- Apple, Disk Utility: create a secure (encrypted) disk image, https://support.apple.com/guide/disk-utility/create-a-disk-image-dskutl11888/mac
- University of Edinburgh Information Security, encrypted disk image on a Mac (256-bit AES), https://infosec.ed.ac.uk/how-to-protect/encrypting/encrypted-containers/mac-create-disk-image
- Apple Platform Security, FileVault volume encryption (AES-XTS), https://support.apple.com/guide/security-pdf/volume-encryption-with-filevault-sec4c6dc1b6e/web
- Apple, corecrypto FIPS 140-3 certifications, https://support.apple.com/guide/certifications/secure-enclave-processor-security-apc3a7433eb89/web

Database crypto on macOS (checked 2026-10-30; see `06` OD-15):
- OpenSSL FIPS provider, https://docs.openssl.org/master/man7/OSSL_PROVIDER-FIPS/
- SQLCipher API (`PRAGMA cipher_fips_status`, `cipher_provider`), https://www.zetetic.net/sqlcipher/sqlcipher-api/
- SQLCipher source, OpenSSL provider, https://github.com/sqlcipher/sqlcipher/blob/master/src/crypto_openssl.c

Compromise check sources:
- NVD, https://nvd.nist.gov
- CISA Known Exploited Vulnerabilities catalog, https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- NIST CMVP, https://csrc.nist.gov/projects/cryptographic-module-validation-program

Unverified: DFARS 252.204-7012, DoDI 5230.24.
