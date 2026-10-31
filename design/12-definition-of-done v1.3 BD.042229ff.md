# 12 Definition of Done (v1)

> **Rough bookmark, not a finished spec.** Start at `00`.
> Revised 2026-10-30: the pilot is done in the WorkOrder app. There is no command-line use.

v1 is done when all of these are true:
1. C0 PASS: every component has a PASS row in `docs/compromise-check.md` with the same version as `requirements.lock`, and every crypto module's CMVP certificate is recorded as Active.
2. C1 PASS: `.gitignore` carries the CUI block, git tracks no blocked file, the software refuses a data location that is missing, inside the repo or unencrypted, the FIPS provider check works, and the no-network test passes.
3. C2 to C11 `pytest` suites PASS, and `ruff` reports no errors.
4. The load step refuses to load without the owner's confirm, with a wrong confirm, with a changed file, or with any mismatch count above 0 (C7), and each refusal is audited.
5. The owner's pilot run, done in the app (one engine system, one symptom, `06` OD-5), reports M1 to M5 all 0 and capabilities 1 to 7 return results, reported to you as counts only. He does not use a terminal for the pilot.
6. The Audit screen's chain check passes and shows the expected event types for the pilot (unlock, unwrap, load, queries), with no CUI in any line.
7. Backup, restore and batch purge (C11) PASS.
8. Every output shown in the pilot carries its marking.
9. You've told the owner in the chat that capabilities 1 to 7 are done. Capabilities 8 to 10 aren't built.
10. No manual content, extracted data, database file or key is in the repo or its history.
