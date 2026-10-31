# 10 Acceptance Tests (one set per build step)

> **Rough bookmark, not a finished spec.** Start at `00`.
> Revised 2026-10-30: rows marked "owner" are actions in the WorkOrder app. He does not use a terminal.

Each test checks the **software's behavior**. You run the `pytest` suites. They call the same functions the screens call. The rows marked "owner" are things only the owner can do in the app because they touch real data or his drives; he tells you the result line (PASS/FAIL, counts, error codes, hashes), never content. A FAIL means fix it before the next step.

| Test | Step | Runs | Command (illustrative) | Expected |
|---|---|---|---|---|
| C0 | Compromise check record | you | `pytest tests/test_compromise_record.py` | every package and version in `requirements.lock`, plus each native tool, has a row in `docs/compromise-check.md` with the same version; each row lists NVD, CISA catalog, vendor advisory and supply-chain sources with a UTC date; every row's result is PASS; every crypto row has a CMVP certificate number with status Active |
| C1 | Repo hygiene | you | `pytest tests/test_repo.py` | `.gitignore` contains every CUI block line from `09`; `git ls-files` lists no file matching them |
| | Data location | you | `pytest tests/test_data_location.py` | the software refuses to start (clear error code) when `WORKORDER_DATA` is unset, points inside the repo, or points at a volume that doesn't report as encrypted (volume info stubbed in the test); temp files go to `tmp/` in the data location; core file size limit is 0 |
| | FIPS provider | you | `pytest tests/test_fips.py` | the software refuses to open the database when the OpenSSL FIPS provider isn't loaded, and proceeds when it is (`06` OD-15) |
| | No network | you | `pytest tests/test_no_network.py` | with sockets blocked, the pipeline and capabilities run without any connection attempt; no module in `src/` imports a network library; under the sandbox profile (`06` OD-17) a test connection attempt is refused |
| | Data location | owner | Status screen | shows: data location encrypted yes, outside repo yes, FIPS provider loaded yes, network sandbox on yes, Spotlight and Time Machine excluded yes |
| C2 | Schema | you | `pytest tests/schema` on an empty throwaway DB in a temp folder | 9 core tables + support tables created; `parts_to_symptoms` is a view; `PRAGMA foreign_key_check` empty; every extracted table has `revision_id, source_page, change_no, marking, batch_id` NOT NULL |
| C3 | Preprocessing | you | `pytest tests/preprocess` | intake rejects non-PDF, encrypted PDF and PDF with JavaScript with exit 10; limit hit gives exit 20 and no output; markings captured before strip; page with no marking gets `CUI` + review flag; PNNORM-1 cases pass |
| C4 | Parsers | you | `pytest tests/parsers` | each parser emits only its tables (`02`); reused callout keyed by (figure, callout); carried figure number flagged; name-only part reference goes to `unresolved_refs.csv` |
| C5 | Reconciliation | you | `pytest tests/reconcile` | M1 to M5 each detected; `mismatches.csv` has IDs only, no text columns; exit 40 when count > 0 |
| C6 | Output and bundle | you | `pytest tests/bundle` | one CSV per loaded table, none for the view; formula-leading cells prefixed `'`; `MARKING.txt` present; manifest covers every file |
| C7 | Load confirm | you | `pytest tests/load_confirm` | load refuses with a clear code when the confirm is missing or wrong, when any file changed after the manifest was made, or when any mismatch count is above 0; each refusal writes an audit row `load_confirm refused`; an accepted confirm records who, when and the manifest sha256 in `load_batches` |
| C8 | Encrypted load and audit | you | `pytest tests/encrypted_db tests/audit` | the DB file doesn't start with the plain SQLite header; `PRAGMA cipher_provider` reports `openssl`; the key is unwrapped only after the hardware-key check (stubbed); each event type in `04` S7 writes one line; the chain verifies; editing or deleting a line breaks the chain check; no line contains anything but IDs, counts, hashes |
| | | owner | Status screen | reports SQLCipher, the FIPS provider and cipher settings |
| C9 | Revision diff | you | `pytest tests/revisions` | order comes from `publication_index`; a parsed block that disagrees becomes a review item; changes in any column are recorded; `current_*` returns the latest |
| C10 | Capabilities 1 to 7 | you | `pytest tests/capabilities` | each rule in `05` gives its expected result; unparsed PMCS threshold shows "check by hand"; unknown lead time gives max "unknown"; every result view shows its marking in the banner |
| | | owner | pilot run (`06` OD-5) | M1 to M5 counts all 0; capability runs return rows; the owner reports counts only |
| C11 | Backup, restore, purge | you + owner | `pytest tests/backup`; owner runs a backup and a restore to a scratch encrypted image | restored DB opens with the owner's key; a purged batch image is gone and its wrapped password deleted; audit rows for each |
