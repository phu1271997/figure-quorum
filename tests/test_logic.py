"""Deterministic-core tests for FigureQuorum (off-chain, no GenVM).

conftest.py installs a `genlayer` stub before these imports run.
"""
import pytest

from contracts import figure_quorum as fq

UE = fq.gl.vm.UserError

REPO = "owner/repo"
COMMIT = "a" * 40


def _url(period, name):
    return f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/datasets/{period}/{name}.md"


def _src(sid, period, name):
    return {"id": sid, "url": _url(period, name), "sha256": "b" * 64}


def test_unit_conversion_is_exact_integer():
    # length base is micrometre: 1 mm = 1000 um, 2.5 cm = 25000 um, 0.001 km = 1000000 um
    assert fq._to_base("1", "mm", "length") == 1000
    assert fq._to_base("2.5", "cm", "length") == 25000
    assert fq._to_base("0.001", "km", "length") == 1000000
    # mass base is milligram: 1 kg = 1_000_000 mg
    assert fq._to_base("1", "kg", "mass") == 1000000


def test_to_base_rejects_bad_grammar():
    with pytest.raises(UE):
        fq._to_base("12.3456", "mm", "length")   # too many decimals
    with pytest.raises(UE):
        fq._to_base("5", "in", "length")          # unit not in family


def test_to_base_rejects_finer_than_base_unit():
    # The base unit is the smallest; a quantity that does not fold to a whole
    # number of base units must be rejected, never silently floored.
    with pytest.raises(UE):
        fq._to_base("5.5", "um", "length")        # 5.5 um is not a whole um
    with pytest.raises(UE):
        fq._to_base("2.5", "mg", "mass")          # 2.5 mg is not a whole mg
    with pytest.raises(UE):
        fq._to_base("0.001", "um", "length")      # finer than base, rejected
    # Exact sub-unit quantities still convert losslessly.
    assert fq._to_base("0.5", "mm", "length") == 500    # 0.5 mm = 500 um exactly
    assert fq._to_base("2.5", "cm", "length") == 25000


def _readings(values_units):
    rows = []
    for i, vu in enumerate(values_units):
        if vu is None:
            rows.append({"index": i, "decision": "MISSING", "value": "", "unit": "", "quote": "", "base": None})
        else:
            v, u = vu
            rows.append({"index": i, "decision": "MEASURED", "value": v, "unit": u,
                         "quote": "q" * 12, "base": fq._to_base(v, u, "length")})
    return {"rows": rows}


def test_fold_drops_outlier_and_trims_mean():
    # three tight readings around 10 mm plus one gross outlier at 900 mm
    readings = _readings([("10", "mm"), ("11", "mm"), ("9", "mm"), ("900", "mm")])
    out = fq._fold("p1", "subj", "length", readings)
    assert out["status"] == "READY"
    assert out["measured_count"] == 4
    assert out["kept_count"] == 3
    assert out["dropped_indexes"] == [3]
    # trimmed mean of 10,11,9 mm = 10 mm = 10000 um
    assert out["consensus_base"] == 10000
    assert out["base_unit"] == "um"


def test_fold_insufficient_when_fewer_than_three_measured():
    readings = _readings([("10", "mm"), ("11", "mm"), None])
    out = fq._fold("p1", "subj", "length", readings)
    assert out["status"] == "INSUFFICIENT"
    assert out["consensus_base"] is None


def test_sources_validation():
    good = [_src("a", "rain-2026-09-01", "a"), _src("b", "rain-2026-09-01", "b"),
            _src("c", "rain-2026-09-01", "c")]
    assert len(fq._read_sources(good, REPO, "rain-2026-09-01")) == 3
    with pytest.raises(UE):
        fq._read_sources(good[:2], REPO, "rain-2026-09-01")          # too few
    with pytest.raises(UE):
        fq._read_sources(good, "other/repo", "rain-2026-09-01")      # wrong repo
    dupe = [_src("a", "p", "a"), _src("a", "p", "b"), _src("c", "p", "c")]
    with pytest.raises(UE):
        fq._read_sources(dupe, REPO, "p")                            # duplicate id
    badhash = [dict(_src("a", "p", "a"), sha256="xyz"), _src("b", "p", "b"), _src("c", "p", "c")]
    with pytest.raises(UE):
        fq._read_sources(badhash, REPO, "p")                         # bad sha grammar


def test_parse_readings_requires_verbatim_quote():
    docs = ["observed daily rainfall total was 12.4 mm at the station"]
    good = {"rows": [{"index": 0, "decision": "MEASURED", "value": "12.4", "unit": "mm",
                      "quote": "observed daily rainfall total"}]}
    out = fq._parse_readings(good, docs, "length")
    assert out["rows"][0]["base"] == 12400
    bad = {"rows": [{"index": 0, "decision": "MEASURED", "value": "12.4", "unit": "mm",
                     "quote": "a quote that is not in the source document"}]}
    with pytest.raises(UE):
        fq._parse_readings(bad, docs, "length")


def test_constructor_records_deployer_as_owner():
    # The deployer (gl.message.sender_address) is pinned as the sole writer.
    fq.gl.message.sender_address = fq.gl.message.sender_address.__class__("0x" + "a" * 40)
    c = fq.Contract.__new__(fq.Contract)
    fq.Contract.__init__(c, REPO, "subj", "observed daily rainfall total", "length")
    assert c.owner == "0x" + "a" * 40
