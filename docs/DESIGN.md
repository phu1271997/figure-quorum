# Design notes - FigureQuorum

## The trust backbone

FigureQuorum answers one hard question: *given several independent written
reports, what single number should the network commit to?* The parts that make
the answer trustworthy:

1. **Source commitment.** A caller cannot point the oracle at an arbitrary URL.
   Every source must live in the contract's fixed `source_repo`, under
   `datasets/<period>/`, pinned to a 40-hex commit, and carry a SHA-256 that
   must match the served bytes. This removes "the page changed under us" and
   "the leader and validators saw different text" as failure modes.

2. **Independent reading.** The leader asks its LLM to read each document on its
   own and emit a strict per-document row. Documents are explicitly framed as
   untrusted data, never instructions (prompt-injection defence).

3. **Deterministic parse.** Before anything reaches consensus the contract
   enforces an exact grammar: a fixed field set, a tight numeric syntax, and
   every quote must be a verbatim substring of the source. Off-grammar
   proposals are rejected deterministically.

4. **Meaning-level validation.** Each validator re-fetches, re-hashes,
   re-parses, then runs a *second, independent* LLM audit that answers true for
   a row only if the reading is the value and unit the full source actually
   supports - and it is told to scrutinise MISSING as hard as MEASURED. The
   proposal is accepted only if every row passes. This is what keeps it from
   being a format-only validator.

5. **Deterministic fold.** The accepted readings are aggregated with pure Python
   so the final number is byte-identical on every node.

## Robust numeric fold

- Exact integer unit conversion via per-family scale tables (length to
  micrometre, mass to milligram, volume to microlitre). No floats ever touch
  chain state; a decimal string is folded as
  `int(whole+frac) * scale // 10**len(frac)`.
- Outlier rejection uses the **median absolute deviation**: centre on the
  median, drop any reading more than `3 * MAD` from it (with a small relative
  floor so a zero MAD does not reject everything), then report the **trimmed
  mean** of the survivors. MAD is the standard robust-statistics choice and
  needs no per-metric tuning.
- `status` is `READY` only with >= 3 surviving inliers, else `INSUFFICIENT`.

## State lifecycle

- Rounds are append-only canonical-JSON entries in a `DynArray[str]`.
- A `TreeMap[str, str]` maps each period slug to its round index and enforces
  single-use, so the same labelled round cannot be replayed.
- `MAX_ROUNDS` bounds storage growth.
- Views return the folded outcome plus the full source and reading record, so a
  downstream contract can both trust the headline and re-audit the inputs.

## Deliberate non-goals

- No frontend - this is a standalone primitive (the Intelligent Contracts
  track), meant to be imported by other contracts and dApps.
- The bundled `datasets/` files are illustrative report shapes, not real
  measurements. Production use needs credibly governed, independently produced
  feeds and a separate collusion-resistance story for the source set itself.
