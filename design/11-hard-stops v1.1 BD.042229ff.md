# 11 When to Tell the Owner

> **Rough bookmark.** This replaces the old hard-stop table. Nothing here halts you behind a signature or a file. A "stop" just means: tell the owner in the chat, and continue when he says so.

## Tell the owner, then continue when he says so
| Situation | What to say in the chat |
|---|---|
| Manual content shows up where you can see it (a file in the repo, a paste, an error message with page text) | Where it showed up (path or message). Stop reading it, don't copy or summarize it. The owner follows `04` S12 |
| Two design files disagree and `00`'s rule doesn't settle it | Both file names, the section names, and one line on the conflict |
| A component fails the compromise check, or no clean version or alternative exists (`08`) | Component, version, and the IDs found (CVE, CISA catalog entry, advisory, or incident) |
| The work order passes its tests | "Work order done. Vehicle details and the other items under Not in v1 in `05` are not built." Build those only when he says which |
| A task seems to need manual content to get right | What you need to know, phrased so the owner can answer with codes, counts or row IDs |

## Tell the owner and keep going
- **An open decision in `06` affects your step.** Build on its Default and say which Default you used. If he picks something else, change it.
- **A real-data run fails.** Ask for error codes, row IDs, counts, page indexes and hashes only. Never ask for manual text.
