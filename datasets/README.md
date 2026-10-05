# datasets/

Source documents, grouped by round:

```
datasets/<period>/<source-id>.md
```

Each file is an untrusted prose report. The contract never runs a file as
instructions - it only reads it as data and lifts out one figure.

## Pinning a source

A source entry passed to `open_round` is:

```json
{"id": "gauge-a", "url": "https://raw.githubusercontent.com/phu1271997/figure-quorum/<commit>/datasets/<period>/gauge-a.md", "sha256": "<digest>"}
```

Rules enforced on chain:

- the `url` must sit inside the contract's fixed `source_repo`;
- the path must be `datasets/<period>/<id>.md`;
- the commit must be a full 40-hex **commit SHA**, never a branch, so the bytes
  cannot change under the hash;
- `sha256` must equal the SHA-256 of the exact bytes served.

## Computing a digest

```bash
git rev-parse HEAD                                       # the 40-hex commit to pin
shasum -a 256 datasets/rain-2026-09-01/gauge-a.md        # the digest to pin
```

The files under `rain-2026-09-01/` are illustrative report shapes, not real
gauge readings. Replace them with credibly governed, independently produced
feeds before using the primitive for anything that matters.
