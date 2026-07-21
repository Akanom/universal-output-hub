from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from scripts.inspect_dist import inspect
from scripts.verify_dependencies import dependency_errors
from universal_output_hub import _optional


def test_dependency_metadata_satisfies_policy() -> None:
    assert dependency_errors(Path(__file__).parents[1]) == []


def test_optional_dependency_error_names_extra(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked_import(name: str) -> object:
        raise ModuleNotFoundError("blocked", name=name)

    monkeypatch.setattr(_optional, "import_module", blocked_import)
    with pytest.raises(ImportError, match=r"universal-output-hub\[excel\]"):
        _optional.require_optional("openpyxl", "excel", "Excel export")


def test_artifact_inspector_rejects_path_traversal(tmp_path: Path) -> None:
    wheel = tmp_path / "unsafe-1-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("../outside.py", "")
    report = inspect(wheel, set(), 250_000_000, 20_000)
    assert any("unsafe archive path" in error for error in report["errors"])


def test_artifact_inspector_rejects_backup_snapshot(tmp_path: Path) -> None:
    wheel = tmp_path / "unsafe-1-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("package/model.before_patch.py", "")
    report = inspect(wheel, set(), 250_000_000, 20_000)
    assert any("sensitive file name" in error for error in report["errors"])
