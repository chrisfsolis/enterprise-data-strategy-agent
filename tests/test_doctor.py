from pathlib import Path

from enterprise_data_strategy_agent.doctor import run_doctor


def test_doctor_detects_repo_root(capsys):
    result = run_doctor(Path.cwd())
    out = capsys.readouterr().out
    assert result == 0
    assert "[OK] Found pyproject.toml" in out


def test_doctor_returns_useful_failure_if_pyproject_missing(tmp_path, capsys):
    result = run_doctor(tmp_path)
    out = capsys.readouterr().out
    assert result == 1
    assert "[ERROR] You are not in the repo root" in out
    assert "pyproject.toml" in out


def test_doctor_checks_required_sample_files(capsys):
    result = run_doctor(Path.cwd())
    out = capsys.readouterr().out
    assert result == 0
    assert "[OK] Found sample inventory" in out
    assert "[OK] Found sample policy" in out
