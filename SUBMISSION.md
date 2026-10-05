# Portal submission - Intelligent Contracts (Builder track)

Repo: https://github.com/phu1271997/figure-quorum
Network: GenLayer Studionet (chain id 61999)
Address: `0xeC8A46C5F3645f756c333fFb776410820207424D`

**Title**
FigureQuorum - consensus unit-exact number from independent prose reports

**Description (<1000 chars)**
FigureQuorum is a reusable GenLayer oracle primitive that turns several
independently published prose reports into one number the whole validator set
agrees on. A caller opens a round with 3 to 7 source documents, each pinned to a
GitHub commit and a SHA-256 hash. Every validator fetches the same bytes,
confirms the hash, and asks its own LLM to read each document and lift out the
figure for a named metric, with a verbatim supporting quote. Consensus is on the
meaning of each reading, not JSON shape: a validator agrees only when its own
independent audit finds every reading is the value and unit the full source
actually supports. The contract then folds the readings deterministically with
exact integer unit conversion, a median-absolute-deviation outlier filter and a
trimmed mean, and stores the round on chain. Parameterised by (repo, subject,
metric, unit family), so one deployment serves KPI, ESG, lab or audit figures.

**Verification (<500 chars)**
Deployed on Studionet at 0xeC8A46C5F3645f756c333fFb776410820207424D (deploy
Result: SUCCESS, get_state reads back the configured metric). Source, README,
design notes and deterministic tests (unit conversion, MAD outlier rejection,
trimmed mean, verbatim-quote and source-commitment validation) at
https://github.com/phu1271997/figure-quorum
