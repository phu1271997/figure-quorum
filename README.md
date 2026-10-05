# FigureQuorum

A standalone **GenLayer Intelligent Contract primitive** that turns several
independently published prose reports into one **unit-exact number** the whole
validator set agrees on.

A caller opens a round with 3..7 source documents. Each document is pinned to a
GitHub commit and a SHA-256 digest. Every validator fetches the same bytes,
confirms the hash, and asks its own LLM to read each document and lift out the
figure for a named metric, with a verbatim supporting quote. The contract then
folds the readings **deterministically** - exact integer unit conversion, a
median-absolute-deviation (MAD) outlier filter, and a trimmed mean - and stores
the round on chain.

> Sibling primitive: [ClaimQuorum](https://github.com/phu1271997/claim-quorum)
> folds categorical **verdicts** the same way FigureQuorum folds numbers.

## Why this is a primitive, not a demo

- **Parameterised at construction** - `(source_repo, subject, metric, family)` -
  so one deployment serves KPI, ESG, lab, field or audit figures. Nothing about
  the use case is hardcoded.
- **Non-determinism is the point.** Strip the web fetch and the LLM reading and
  there is no primitive left; the whole value is distilling a defensible number
  from unstructured human text.
- **The validator checks meaning, not shape.** Each validator re-fetches every
  document, re-hashes the bytes, re-parses the proposal deterministically, then
  runs an *independent* LLM audit that answers true for a reading only if it is
  the value and unit the full source actually supports, backed by its quote. Two
  nodes that would read a source differently do **not** agree; a reading that
  merely has the right JSON keys does not pass.

## How consensus works

1. A caller opens a round with 3..7 sources. Each is `{id, url, sha256}` and the
   `url` must be a commit-pinned raw GitHub file inside the fixed `source_repo`,
   under `datasets/<period>/...md`.
2. **Leader** fetches each document, verifies size and `sha256`, then asks its
   LLM to read every document independently and emit one row per document: a
   MEASURED figure (exact decimal + unit + verbatim quote) or MISSING.
3. The contract **parses the proposal deterministically** - strict field set,
   exact numeric grammar, and every quote must be a verbatim span of the source.
4. **Validators** repeat fetch + hash + parse, then run a second independent LLM
   audit of each row against the full source. Accepted only if every row passes
   for every validator.
5. The accepted readings are folded deterministically: convert each to an
   integer base unit, centre on the median, drop readings more than `3 * MAD`
   away, report the trimmed mean of the survivors. `status` is `READY` only with
   >= 3 inliers, else `INSUFFICIENT`.

## Public API

- `open_round(period: str, sources_json: str)` - run a new round.
- `get_latest() -> dict`
- `get_round(index: int) -> dict`
- `get_round_by_period(period: str) -> dict`
- `get_state() -> dict`

`sources_json` is a JSON array:

```json
[
  {"id":"gauge-a","url":"https://raw.githubusercontent.com/phu1271997/figure-quorum/<40-hex-commit>/datasets/rain-2026-09-01/gauge-a.md","sha256":"<64 hex>"},
  {"id":"gauge-b","url":"https://raw.githubusercontent.com/phu1271997/figure-quorum/<40-hex-commit>/datasets/rain-2026-09-01/gauge-b.md","sha256":"<64 hex>"},
  {"id":"gauge-c","url":"https://raw.githubusercontent.com/phu1271997/figure-quorum/<40-hex-commit>/datasets/rain-2026-09-01/gauge-c.md","sha256":"<64 hex>"}
]
```

Pin the commit (not a branch) so the bytes can never change under the hash. See
[`datasets/README.md`](datasets/README.md).

## Unit families

Integer-exact conversion, no floats on chain:

| family | units | base |
|---|---|---|
| length | km, m, cm, mm, um | micrometre (um) |
| mass | t, kg, g, mg | milligram (mg) |
| volume | kl, l, ml, ul | microlitre (ul) |

## Deployed on Studionet

- Address: `0xeC8A46C5F3645f756c333fFb776410820207424D`
- source_repo: `phu1271997/figure-quorum`
- Network: GenLayer Studionet (chain id `61999`, RPC `https://studio.genlayer.com/api`)
- Explorer: <https://explorer-studio.genlayer.com/address/0xeC8A46C5F3645f756c333fFb776410820207424D>

## Develop

```bash
pip install -r requirements.txt
python3 scripts/deploy.py --check-only       # validate schema, no key needed

source ~/.genlayer/env.sh                     # exports GENLAYER_PRIVATE_KEY
python3 scripts/deploy.py                      # deploy to studionet

pytest -q                                      # deterministic aggregation tests
```

[`tests/test_logic.py`](tests/test_logic.py) covers exact unit conversion, MAD
outlier rejection and the trimmed mean, insufficient-data handling,
verbatim-quote enforcement, and source-commitment validation.

## License

MIT - see [LICENSE](LICENSE).
