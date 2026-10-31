# 04 Data Protection and Encryption (CUI)

> **Rough bookmark, not a finished spec.** Start at `00`. Everything below is something **the software** must do, or a setup step the owner follows (you write those steps into `docs/data-setup.md`). You never need manual content for any of it. Sources are at the end; anything not fetched and confirmed is marked unverified.
> Revised 2026-10-30: protections apply to the Mac desktop app. Owner setup steps are Disk Utility, System Settings, and the app's own screens. They are not a terminal session.

The source manuals are **CUI** (Controlled Unclassified Information), not classified.

## S1. Data stays out of the repo and out of AI tools
- Manuals, extracted records, review bundles, the database, keys and the audit log live only in the encrypted data location (`09`), never in the repo. `.gitignore` blocks them and a test checks git tracks none of them (`10` C1).
- Real-data problems come back to you only as error codes, row IDs, counts, page indexes and hashes. Nobody pastes manual text, page images or CSV cells into Grok Build or any AI tool.
- "No AI touches manual content" means the software is deterministic code with no model calls.

## S2. Deployment host and export control
- `06` OD-2 is closed by Adam. The deployment host is not a personal computer; the host type is set by Adam. The no-transmission controls stay as they are: no network code (S3), no cloud sync or AI tools (S1, S8), offline backups (S9) and the compromise check (S11).
- Military maintenance manuals are generally ITAR technical data ("information ... required for the ... operation, repair, testing, maintenance": 22 CFR 120.33(a)(1)). So: only U.S. persons with a need to know use the software; content never goes to any cloud service, AI model or foreign-hosted tool; the export warning is captured and carried (S6). DoDI 5230.24 distribution statements are captured as text (that rule itself is unverified here).

## S3. Network
- The software contains no network code: no sockets, HTTP clients or remote calls, and no dependency that phones home. A test runs the pipeline and the capabilities with networking blocked and fails on any connection attempt (`10` C1).
- The OS also blocks it: the WorkOrder app restarts itself under a macOS sandbox profile that denies all network access before it shows a window, so even a bad dependency can't send anything (`06` OD-17). The profile allows drawing the window and reading and writing the data location. It does not allow a shell, a browser, or outbound sockets. The PDF parser child process gets the same network block (`02`, OD-16). Deny by default: SP 800-171 03.13.06.

## S4. Storage and crypto
- **Baseline:** FileVault is on for the startup disk.
- **Data location:** an encrypted APFS volume ("APFS (Encrypted)" in Disk Utility) or an encrypted disk image (256-bit AES), created and mounted by the owner (`09`, `06` OD-18). On first launch the app asks for that volume and saves only the path, outside the repo. Later launches read the saved path. Tests set `WORKORDER_DATA` instead. The software checks at startup that the path is on an encrypted volume and is not inside the repo, and refuses to open the database otherwise. The check reads volume info on macOS. Confirm the exact field against `diskutil info -plist` when you write the check. The owner does not run that command.
- **Database:** SQLCipher 4 in the data location (`06` OD-3). AES-256, with a random 256-bit database key that is never typed and never stored in plain text.
- **FIPS 140-3:** CUI confidentiality uses FIPS-validated crypto (03.13.11). SQLCipher is built on the OpenSSL FIPS provider (`06` OD-4, closed: industry-standard pick). macOS has no OS-wide FIPS mode, so the software confirms at startup that the OpenSSL FIPS provider is loaded and refuses to open the database otherwise. How that is built and checked on macOS is `06` OD-15. The provider's NIST CMVP certificate must show Active (S11).

## S5. Login and keys
- **Who uses it:** the owner only (`06` OD-19). He unlocks the app with his own FIDO2 hardware key and PIN (03.05.03). Two people he names hold recovery shares. They do not have app access and do not unlock the database in normal use.
- **Unlock before decrypt:** the database key is stored only wrapped (`keys/` in the data location). It is unwrapped only after the owner's hardware-key check (FIDO2 `hmac-secret`). There is no shared passphrase and no second operator key.
- **Idle lock:** the session locks after 15 minutes idle and the database key is wiped from memory (03.01.10, 03.01.11).
- **Inside the database:** SQLCipher has one key per file, so anyone who can open it can read every table. The software limits what queries can do instead: read-only connections for queries, writes only through the load step. All the data is CUI with the same audience, so per-table secrecy isn't needed.
- **Rotation:** rekey the database (`PRAGMA rekey`) once a year, when the hardware key is replaced, or when a key may be compromised. Re-wrap the owner's copy, and audit the event.
- **Recovery:** a recovery copy of the database key is split 2-of-3 (Shamir) between the owner and two people he names, on paper or offline media, stored in separate locked places. Recovery takes two people and is audited. Without recovery, a lost hardware key means lost data.

## S6. Markings (captured before strip, carried everywhere)
- Captured in `02` step 3: banner, portion markings, designation indicator, CUI categories, distribution statement, export warning (32 CFR 2002.20(b), 2002.20(g); DoDI 5200.48 3.4.a, 3.4.f).
- Stored on every row (`marking`) and on `manual_revisions`.
- **Outputs:** every CSV has a `marking` column and every review bundle carries `MARKING.txt`. Every window that shows rows has a banner at the top and the bottom with the highest marking of those rows, plus the distribution statement and export warning. Reports keep the designation indicator. Unknown marking = treated as CUI. A file with a marking above CUI: see `06` OD-13.

## S7. The audit log
- `audit.jsonl` in the data location, written only by the software, opened in append mode. Each line carries `prev_hash` (SHA-256 of the previous line), so any edit or deletion breaks the chain (03.03.08).
- Each line: UTC timestamp, macOS user, event, object IDs and hashes, result, `prev_hash`. **No CUI**: no manual text, part descriptions, thresholds or query parameters; IDs, counts and hashes only (03.03.02).
- **Events:** unlock success and failure, every key unwrap (= every decryption), DB open and close, capability query (capability number and row count), pipeline start and finish per file, intake reject, load confirm (accepted or refused), load, override applied, export or copy of any CUI file, backup, restore, purge, key rotation, recovery, chain-check result (03.03.02; 03.03.07 time stamps).
- The Audit screen runs the chain check and shows the head hash (`05`). The owner runs it weekly and writes the head hash on paper (03.03.03 review). Retention: `06` OD-10.

## S8. Copies and leak paths (everything derived is CUI)
- Intermediates, CSVs, review bundles, mismatch files, diffs, logs and backups are as sensitive as the source PDFs. They live only in the data location or on encrypted backup drives.
- The software points its temp directory at `tmp/` in the data location, and the parser child process too. It turns off core dumps for itself and its children (core file size limit 0).
- The data location is excluded from Spotlight and from Time Machine, and is never under `~/Desktop`, `~/Documents` or any iCloud, Dropbox or other sync folder. `docs/data-setup.md` gives the owner the exact steps; confirm the commands with the macOS man pages (`mdutil`, `tmutil`).
- The app takes query inputs in its own fields. File picks stay inside the data location. It has no command-line interface, so inputs never land in a shell history.
- Review uses the app's Review screen only (`05`, `08`). No Quick Look, Preview, office suite, browser, web view, or cloud preview opens CUI.
- The app does not print, share, or hand a PDF to another program. Copy places only an explicitly selected part number (`part_number_norm`) on the pasteboard. Lock and quit clear that copy. `docs/data-setup.md` tells the owner to turn Universal Clipboard off.
- No `.bak` copies or ad-hoc exports. The only copies are the backups in S9.

## S9. Backups
- Backups are the SQLCipher file (already encrypted) plus the audit log, written to an **encrypted external drive** (APFS (Encrypted)) with its own password, never to the cloud, Time Machine or network shares (03.08.09, 03.13.08).
- Each backup drive is labeled CUI, listed in an inventory, and stored locked (03.08.03, 03.08.04 markings on media).
- Monthly restore test into a scratch encrypted disk image, which is then deleted along with its password. Backup and restore are audited.

## S10. Purge and sanitization (NIST SP 800-88 Rev 2)
- Each batch's work area (`batches/<batch>/` in the data location) is its own encrypted disk image (256-bit AES) with a random password that is stored only wrapped under the database key. After a validated load, purge = detach the image, delete the image file and delete its wrapped password (crypto erase: without the password the image can't be opened). Purge is audited with the image hash.
- End-of-life drives (data location and backup drives): crypto erase or physical destruction per SP 800-88 Rev 2, with a record (03.08.03 sanitize before disposal).
- Old revisions in the database are kept for audit, not purged, until the retention period in `06` OD-10.

## S11. Supply chain and the compromise check
- Every Python dependency is pinned with its sha256 in `requirements.lock` and installed with `pip install --require-hashes -r requirements.lock` (03.17.01, 03.17.03). Native tools (Tesseract, SQLCipher, the OpenSSL FIPS provider) are pinned to exact versions in `docs/compromise-check.md`.
- **Compromise check (required).** Before any tool, library or dependency is used, check that exact version for known compromise, and check again whenever a dependency is added or changed and before the first real-data run. You (Grok Build) do the lookups; the owner can re-run them. Public data only:
  1. NVD: no unpatched CVE affects the version (none known-exploited, none critical or high).
  2. CISA Known Exploited Vulnerabilities catalog: the component isn't listed, or the version has the fix.
  3. Vendor or project security advisories (OpenSSL, SQLCipher, Python, Tesseract, each library): none open against the version.
  4. Supply-chain incidents (malicious release, compromised maintainer or signing key, tampered package or mirror): none reported for the component or its source.
  5. Every crypto module (the OpenSSL FIPS provider; Apple corecrypto behind the encrypted APFS volume): its NIST CMVP certificate is Active, not Revoked or Historical. Record the certificate number.
  6. Downloaded files match their published hash or upstream signature where the project provides one.
- **Record:** one row per component in `docs/compromise-check.md`: component, version, sources checked (URL and UTC date), findings (CVE IDs with severity, CISA catalog status, advisory IDs, incident reports, CMVP certificate number and status, or "none found"), result PASS or FAIL. A FAIL means pick a patched version or an alternative and check that one; if none is clean, tell the owner in the chat (`11`).
- The PDF parser runs in a separate child process with limits (`02`, `06` OD-16), because a malformed PDF is an attack surface.

## S12. Spill and incident procedure
**Triggers:** CUI found outside the data location or a backup drive (in the repo, in a chat, in a log); any manual content reaching Grok Build, an AI tool or the cloud; a lost or stolen drive or hardware key; an audit chain break; a file with a marking above CUI.
**Steps:**
1. Stop the software and disconnect the network.
2. Don't delete anything yet; preserve the evidence.
3. Write down time (local and UTC), what, where, and who.
4. The owner is told at once.
5. The owner reports to the contract's CUI authority or contracting officer within the contract's deadline (DFARS 252.204-7012 sets 72 hours: **unverified**) (03.06.02; DoDI 5200.48 3.9.e).
6. Sanitize only as that authority directs (S10).
7. Rotate any affected key (S5).
8. Write a short post-incident note: IDs and hashes, no CUI.

## Sources
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

Unverified: DFARS 252.204-7012, DoDI 5230.24. CMVP certificate status is confirmed by the compromise check, not here.
