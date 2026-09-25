import json
import shutil
from pathlib import Path

from sales_pipeline.cli import main

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_generate_then_validate_then_export(tmp_path, monkeypatch):
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    raw = tmp_path / "raw"
    out = tmp_path / "dashboard.json"

    assert main(["generate", "2026-09-01", "2026-09-03", "--raw-dir", str(raw)]) == 0
    assert len(list(raw.glob("*.csv"))) == 3

    assert main(["validate", "--raw-dir", str(raw)]) == 0
    assert main(["export", "--raw-dir", str(raw), "--out", str(out)]) == 0

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schemaVersion"] == 1
    assert payload["range"] == {"from": "2026-09-01", "to": "2026-09-03", "days": 3}
    assert payload["kpis"]["date"] == "2026-09-03"
    assert len(payload["daily"]) == 3
    assert payload["quality"]["status"] == "passed"
    assert "Data quality check passed" in summary.read_text(encoding="utf-8")


def test_validate_fails_on_bad_data(tmp_path, monkeypatch, capsys):
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    raw = tmp_path / "raw"
    raw.mkdir()
    for f in (DATA_DIR / "samples").glob("*.csv"):
        shutil.copy(f, raw)

    assert main(["validate", "--raw-dir", str(raw)]) == 1
    out = capsys.readouterr().out
    assert "DATA QUALITY CHECK FAILED" in out
    assert "::error" in out
    assert "Deployment blocked" in summary.read_text(encoding="utf-8")


def test_validate_fails_on_empty_folder(tmp_path):
    assert main(["validate", "--raw-dir", str(tmp_path)]) == 1


def test_export_includes_build_metadata_in_ci(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    main(["generate", "2026-09-01", "--raw-dir", str(raw)])
    monkeypatch.setenv("GITHUB_SHA", "abcdef1234567")
    monkeypatch.setenv("GITHUB_RUN_NUMBER", "42")
    monkeypatch.setenv("GITHUB_RUN_ID", "999")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_REPOSITORY", "me/sales-pulse")
    out = tmp_path / "d.json"
    main(["export", "--raw-dir", str(raw), "--out", str(out)])
    build = json.loads(out.read_text(encoding="utf-8"))["build"]
    assert build == {
        "commit": "abcdef1",
        "runNumber": "42",
        "runUrl": "https://github.com/me/sales-pulse/actions/runs/999",
    }
