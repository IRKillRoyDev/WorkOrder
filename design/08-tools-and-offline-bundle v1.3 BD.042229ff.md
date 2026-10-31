# 08 Tools and the Compromise Check

> **Rough bookmark, not a finished spec.** Start at `00`. There is no offline bundle any more: you install dependencies into the repo's `.venv/` from the normal package sources, pinned by hash, after each one passes the compromise check.
> Revised 2026-10-30: the review viewer is the app's Review screen. The terminal viewer is gone.

## Tool picks
Every pick is provisional until its row in `docs/compromise-check.md` shows PASS (`04` S11). Exact versions live in `requirements.lock` (Python packages, with sha256 hashes) and in `docs/compromise-check.md` (everything else). Those files, not this table, are the version authority.
| Need | Pick | Where it comes from |
|---|---|---|
| OS | macOS (`06` OD-1); the deployment host is set by the owner (OD-2) | already installed |
| Language | Python 3.12, virtual environment at `.venv/` in the repo | python.org installer or Homebrew |
| PDF text and tables | `pdfplumber` (text layer, table extraction), `pypdfium2` (page render for OCR) | PyPI wheels |
| PDF intake cleanup | `pikepdf` (drop actions, JavaScript, embedded files, annotations, forms, metadata) | PyPI wheel |
| OCR | Tesseract 5 with English data, called through `pytesseract` | Homebrew `tesseract` + PyPI wheel |
| Database | SQLCipher 4 built from a pinned source tag against OpenSSL 3 with the FIPS provider (`06` OD-4 closed; macOS build in OD-15), Python binding `sqlcipher3` built against it | source tarballs, built by a script in `scripts/` |
| Hardware key unwrap | FIDO2 key with `hmac-secret`, through `python-fido2` | PyPI wheel |
| Recovery split | a Shamir 2-of-3 tool or library (Default `ssss`) | picked through the compromise check |
| Desktop windows | PySide6, macOS widget style (`06` OD-20). No Qt WebEngine and no import of QtNetwork. `scripts/` builds `WorkOrder.app` from this | PyPI wheel |
| Lock file | `pip-tools` (`pip-compile --generate-hashes`) | PyPI wheel |
| Tests and lint | `pytest`, `ruff` | PyPI wheels |
| Version control | `git` | already installed |
Anything else needs its own compromise-check row first.

## Install
1. Write `requirements.in`, then generate `requirements.lock` with `pip-compile --generate-hashes`.
2. Install with `pip install --require-hashes -r requirements.lock` into `.venv/`. Hash mismatches fail the install.
3. Build SQLCipher and `sqlcipher3` with the script in `scripts/` (`06` OD-15).

## Compromise check (before you use anything)
For every tool, library and dependency above, every package in `requirements.lock`, and the native builds: run the checks in `04` S11 (NVD, CISA Known Exploited Vulnerabilities catalog, vendor advisories, supply-chain incidents, CMVP certificate status for crypto modules, published hashes or signatures) and write one row per component in `docs/compromise-check.md`.

**Decision rule.** A component with an unpatched known-exploited CVE (CISA catalog) or an unpatched critical or high CVE affecting the version isn't used: pick a patched version or an alternative and check that one. A crypto module without an Active CMVP certificate isn't used. If no clean version or alternative exists, tell the owner in the chat (`11`).

**When.** Before first use, whenever a dependency is added or its version changes, and again before the first real-data run. A test checks that every component in `requirements.lock` has a PASS row with the same version (`10` C0).
