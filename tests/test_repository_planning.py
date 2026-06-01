import pytest

from devsecscan.models.repository_structure import DirectoryType, RepositoryStructure
from devsecscan.models.scan_plan import RepositoryScanSummary
from devsecscan.repository.directory_classifier import (
    DIRECTORY_PRIORITIES,
    KNOWN_DIRECTORIES,
    DirectoryClassifier,
)
from devsecscan.repository.ignore_loader import IgnoreLoader
from devsecscan.repository.repository_mapper import RepositoryMapper, RepositoryMappingError
from devsecscan.repository.scan_plan import format_repository_scan_summary
from devsecscan.repository.scan_planner import ScanPlanner
from devsecscan.scanners.file_scanner import FileScanner
from devsecscan.security_detectors.secret_detector import SecretDetector
from devsecscan.models.domain import RepositoryContext


def test_directory_classifier_known_registry_and_extensibility():
    classifier = DirectoryClassifier({"custom_src": DirectoryType.SOURCE_CODE})

    assert KNOWN_DIRECTORIES["node_modules"] == DirectoryType.DEPENDENCIES
    assert classifier.classify("src") == DirectoryType.SOURCE_CODE
    assert classifier.classify("tests") == DirectoryType.TEST_CODE
    assert classifier.classify("node_modules") == DirectoryType.DEPENDENCIES
    assert classifier.classify("venv") == DirectoryType.ENVIRONMENT
    assert classifier.classify(".git") == DirectoryType.METADATA
    assert classifier.classify("custom_src") == DirectoryType.SOURCE_CODE
    assert classifier.classify("mystery") == DirectoryType.UNKNOWN


def test_directory_scoring_prioritizes_source_and_config():
    classifier = DirectoryClassifier()

    assert DIRECTORY_PRIORITIES[DirectoryType.SOURCE_CODE] == 100
    assert classifier.priority_for(DirectoryType.CONFIGURATION) == 90
    assert classifier.priority_for(DirectoryType.TEST_CODE) == 40
    assert classifier.priority_for(DirectoryType.DOCUMENTATION) == 10
    assert classifier.priority_for(DirectoryType.DEPENDENCIES) == 0


def test_repository_mapper_discovers_top_level_only_and_classifies(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "nested").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")

    structure = RepositoryMapper().map(tmp_path)

    assert structure.directories == ["node_modules", "src"]
    assert structure.files == ["pyproject.toml"]
    assert structure.directory_types["src"] == DirectoryType.SOURCE_CODE
    assert structure.directory_types["node_modules"] == DirectoryType.DEPENDENCIES
    assert "nested" not in structure.directories


def test_repository_mapper_missing_repository_raises():
    with pytest.raises(RepositoryMappingError):
        RepositoryMapper().map("path-that-does-not-exist")


def test_repository_mapper_skips_broken_symlink(tmp_path):
    broken = tmp_path / "broken"
    try:
        broken.symlink_to(tmp_path / "missing", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is not available")

    structure = RepositoryMapper().map(tmp_path)

    assert "broken" not in structure.directories
    assert "broken" not in structure.files


def test_ignore_loader_supports_devsecscanignore_patterns(tmp_path):
    (tmp_path / ".devsecscanignore").write_text("# comment\nlegacy/\n*.tmp\n")
    loader = IgnoreLoader()
    patterns = loader.load(tmp_path)

    assert patterns == ["legacy/", "*.tmp"]
    assert loader.matches("legacy/app.py", patterns) is True
    assert loader.matches("debug.tmp", patterns) is True
    assert loader.matches("src/app.py", patterns) is False


def test_ignore_loader_gracefully_falls_back_on_read_error(tmp_path, monkeypatch):
    (tmp_path / ".devsecscanignore").write_text("legacy/\n")

    def broken_open(*args, **kwargs):
        raise OSError("cannot read")

    monkeypatch.setattr("builtins.open", broken_open)

    assert IgnoreLoader().load(tmp_path) == []


def test_scan_planner_builds_plan_with_skips_priorities_and_root_files(tmp_path):
    for dirname in ["src", "api", "tests", "node_modules", "venv", ".git", "build", "docs"]:
        (tmp_path / dirname).mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    (tmp_path / ".devsecscanignore").write_text("api/\n")

    plan = ScanPlanner().plan(tmp_path)

    assert plan.scan_directories == ["src"]
    assert plan.skip_directories == [".git", "api", "build", "docs", "node_modules", "tests", "venv"]
    assert "pyproject.toml" in plan.scan_files
    assert plan.directory_priorities["src"] == 100
    assert plan.directory_priorities["api"] == 100
    assert plan.skip_reasons["api"] == "matched .devsecscanignore"
    assert "dependency directories" in plan.skip_reasons["node_modules"]
    assert "scan_directories" in plan.model_dump_json()



def test_scan_planner_from_structure_and_summary_formatting(tmp_path):
    structure = RepositoryStructure(
        project_path=str(tmp_path),
        directories=["src", "dist"],
        files=["main.py"],
        directory_types={
            "src": DirectoryType.SOURCE_CODE,
            "dist": DirectoryType.BUILD_OUTPUT,
        },
    )

    planner = ScanPlanner()
    plan = planner.from_structure(structure)
    summary = planner.summarize(plan)
    output = format_repository_scan_summary(summary)

    assert isinstance(summary, RepositoryScanSummary)
    assert summary.directories_found == 2
    assert "Scannable Directories:\n* src" in output
    assert "Ignored Directories:\n* dist" in output
    assert "Reason:" in output


def test_file_scanner_uses_scan_plan_as_allowed_surface(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    skipped = tmp_path / "generated"
    skipped.mkdir()
    (src / "safe.py").write_text("print('scan me')\n")
    (skipped / "secret.py").write_text('OPENAI_API_KEY = "sk-1234567890abcdefghijk1234567890"\n')
    (tmp_path / ".devsecscanignore").write_text("generated/\n")

    plan = ScanPlanner().plan(tmp_path)
    scanned = list(FileScanner().scan(tmp_path, plan))
    scanned_paths = {path.relative_to(tmp_path).as_posix() for path, _, _ in scanned}

    assert "src/safe.py" in scanned_paths
    assert "generated/secret.py" not in scanned_paths


def test_secret_detector_uses_context_scan_plan(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    skipped = tmp_path / "legacy"
    skipped.mkdir()
    (src / "config.py").write_text('OPENAI_API_KEY = "sk-1234567890abcdefghijk1234567890"\n')
    (skipped / "config.py").write_text('AWS_KEY = "AKIA1234567890123456"\n')
    (tmp_path / ".devsecscanignore").write_text("legacy/\n")

    plan = ScanPlanner().plan(tmp_path)
    context = RepositoryContext(project_path=str(tmp_path), scan_plan=plan)
    findings = SecretDetector().detect(context)

    assert len(findings) == 1
    assert findings[0].file_path.replace("\\", "/") == "src/config.py"
