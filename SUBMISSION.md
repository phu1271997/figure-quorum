# Portal submission - Intelligent Contracts (Builder track)

Repo: https://github.com/phu1271997/figure-quorum
Network: GenLayer Studionet (chain id 61999)
Address: `0x6cb85d252C2f88E7A95494b45382361d69f77562`

**Title**
FigureQuorum - consensus unit-exact number from independent prose reports

**Description (<1000 chars)**
FigureQuorum is a reusable GenLayer oracle primitive that turns several
independently published prose reports into one number the whole validator set
agrees on. The owner opens a round with 3 to 7 source documents, each pinned to a
GitHub commit and a SHA-256 hash. Every validator fetches the same bytes,
confirms the hash, and asks its own LLM to lift out the figure for a named
metric with a verbatim quote. Consensus is on meaning, not JSON shape: a
validator agrees only when its own independent audit finds every reading is the
value and unit the full source supports. The contract then folds the readings
deterministically with exact integer unit conversion, a MAD outlier filter and a
trimmed mean. Only the owner may open rounds and the log is append-only and
unbounded, so no caller can squat a period label or exhaust a capacity; a
quantity finer than the base unit is rejected, never silently floored.
Parameterised by (repo, subject, metric, unit family).

**Verification (<500 chars)**
Deployed on Studionet at 0x6cb85d252C2f88E7A95494b45382361d69f77562 (deploy
Result: SUCCESS, get_state reads back the configured metric). Source, README,
design notes and deterministic tests (unit conversion, MAD outlier rejection,
trimmed mean, verbatim-quote and source-commitment validation) at
https://github.com/phu1271997/figure-quorum
