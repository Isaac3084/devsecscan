import pytest
import os
from pathlib import Path
from devsecscan.scanners.file_scanner import FileScanner

def test_file_scanner_text_files(tmp_path):
    (tmp_path / "valid.py").write_text("print('hello')\nprint('world')")
    (tmp_path / "ignored.md").write_text("markdown") # Not in default extensions
    
    scanner = FileScanner()
    lines = list(scanner.scan(tmp_path))
    
    assert len(lines) == 2
    assert lines[0][0].name == "valid.py"
    assert lines[0][1] == 1
    assert "hello" in lines[0][2]

def test_file_scanner_binary_files(tmp_path):
    # Create a fake binary file
    bin_file = tmp_path / "app.exe"
    with open(bin_file, "wb") as f:
        f.write(b"hello\0world")
    
    # We have to allow .exe to test the binary skip, or test directly on is_binary
    scanner = FileScanner()
    assert scanner.is_binary(bin_file) is True
    
    txt_file = tmp_path / "app.py"
    with open(txt_file, "wb") as f:
        f.write(b"hello world")
    assert scanner.is_binary(txt_file) is False

def test_file_scanner_large_files(tmp_path):
    large_file = tmp_path / "large.py"
    # Create a 2MB file
    with open(large_file, "wb") as f:
        f.write(b"a" * 2_000_000)
    
    scanner = FileScanner(max_file_size_bytes=1_000_000)
    lines = list(scanner.scan(tmp_path))
    assert len(lines) == 0

def test_file_scanner_ignores_dirs(tmp_path):
    node_modules = tmp_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "bad.js").write_text("console.log()")
    
    scanner = FileScanner()
    lines = list(scanner.scan(tmp_path))
    assert len(lines) == 0
