import pytest
from pathlib import Path
from devsecscan.scanners.ignore_manager import IgnoreManager
from devsecscan.scanners.file_scanner import FileScanner


class TestIgnoreManager:
    def test_default_ignores_tests_dir(self, tmp_path):
        mgr = IgnoreManager(tmp_path)
        test_file = tmp_path / "tests" / "test_foo.py"
        assert mgr.should_ignore(test_file, tmp_path) is True

    def test_default_ignores_node_modules(self, tmp_path):
        mgr = IgnoreManager(tmp_path)
        nm_file = tmp_path / "node_modules" / "react" / "index.js"
        assert mgr.should_ignore(nm_file, tmp_path) is True

    def test_does_not_ignore_source(self, tmp_path):
        mgr = IgnoreManager(tmp_path)
        src_file = tmp_path / "src" / "main.py"
        assert mgr.should_ignore(src_file, tmp_path) is False

    def test_custom_ignore_file(self, tmp_path):
        (tmp_path / ".devsecscanignore").write_text("*.log\nsecrets/\n# comment line\n")
        mgr = IgnoreManager(tmp_path)

        log_file = tmp_path / "app.log"
        assert mgr.should_ignore(log_file, tmp_path) is True

        secrets_file = tmp_path / "secrets" / "creds.json"
        assert mgr.should_ignore(secrets_file, tmp_path) is True

        src_file = tmp_path / "src" / "main.py"
        assert mgr.should_ignore(src_file, tmp_path) is False

    def test_comments_and_empty_lines(self, tmp_path):
        (tmp_path / ".devsecscanignore").write_text("# this is a comment\n\n*.tmp\n")
        mgr = IgnoreManager(tmp_path)
        assert len(mgr._patterns) > 0
        assert "# this is a comment" not in mgr._patterns


class TestFileScannerIgnores:
    def test_scanner_skips_tests_dir(self, tmp_path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_secrets.py").write_text('API_KEY = "sk-fake12345678901234567890"')

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text('print("hello")')

        scanner = FileScanner()
        scanned_files = set()
        for fp, _, _ in scanner.scan(tmp_path):
            scanned_files.add(fp.name)

        assert "main.py" in scanned_files
        assert "test_secrets.py" not in scanned_files

    def test_scanner_respects_devsecscanignore(self, tmp_path):
        (tmp_path / ".devsecscanignore").write_text("secrets/\n")
        secrets_dir = tmp_path / "secrets"
        secrets_dir.mkdir()
        (secrets_dir / "keys.json").write_text('{"key": "value"}')

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "app.py").write_text('print("safe")')

        scanner = FileScanner()
        scanned_files = set()
        for fp, _, _ in scanner.scan(tmp_path):
            scanned_files.add(fp.name)

        assert "app.py" in scanned_files
        assert "keys.json" not in scanned_files
