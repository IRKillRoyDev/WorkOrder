# 12 Definition of Done (v1)

> **Rough bookmark, not a finished spec.** Start at `00`.
> Revised 2026-10-31: v1 encrypts the database file and unlocks it with a passphrase. It does not encrypt the disk and it does not use a hardware key or SSH.

v1 is done when all of these are true:
1. C0 PASS: every component has a PASS row in `docs/compromise-check.md` with the same version as `requirements.lock`. A missing FIPS certificate does not fail C0.
2. C1 PASS: `.gitignore` carries the CUI block, git tracks no blocked file, the software refuses a data folder that is missing or inside the repo, an unencrypted disk is allowed, the passphrase unlocks the database and a wrong passphrase does not, and the no-network test passes.
3. C2 to C11 `pytest` suites PASS, and `ruff` reports no errors.
4. The load step refuses to load without the owner's confirm, with a wrong confirm, with a changed file, or with any mismatch count above 0 (C7), and each refusal is audited.
5. The owner's pilot, done in the app (`06` OD-5), opens one work order, selects issues from the troubleshooting manual, and shows a time-to-repair estimate. He reports counts only. He does not use a terminal for the pilot.
6. The Audit screen's chain check passes and shows the expected event types for the pilot (unlock, load, work order), with no CUI in any line.
7. Backup, restore and batch purge (C11) PASS.
8. Every output shown in the pilot carries its marking.
9. You've told the owner in the chat that the work order is done. Vehicle details and the other items under "Not in v1" in `05` are not built.
10. No manual content, extracted data, database file or key is in the repo or its history.
