import pytest
from pathlib import Path
import json
from devsecscan.detectors.language_detector import LanguageDetector
from devsecscan.detectors.framework_detector import FrameworkDetector
from devsecscan.detectors.package_manager_detector import PackageManagerDetector
from devsecscan.detectors.dependency_detector import DependencyDetector

def test_language_detector_empty(tmp_path):
    detector = LanguageDetector()
    scores = detector.detect(tmp_path)
    assert scores == {}
    assert detector.get_primary_language(scores) is None

def test_language_detector_mixed(tmp_path):
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "utils.py").write_text("def x(): pass")
    (tmp_path / "script.js").write_text("console.log('hello')")
    
    detector = LanguageDetector()
    scores = detector.detect(tmp_path)
    assert scores["python"] == 0.67
    assert scores["javascript"] == 0.33
    assert detector.get_primary_language(scores) == "python"

def test_framework_detector():
    detector = FrameworkDetector()
    assert detector.detect(["fastapi", "uvicorn"]) == "fastapi"
    assert detector.detect(["react", "react-dom"]) == "react"
    assert detector.detect(["next", "react"]) == "next.js" # next has priority if it exists
    assert detector.detect(["unknown-dep"]) is None

def test_package_manager_detector(tmp_path):
    detector = PackageManagerDetector()
    assert detector.detect(tmp_path) is None
    
    (tmp_path / "poetry.lock").touch()
    assert detector.detect(tmp_path) == "poetry"
    
    # Clean up and test npm
    (tmp_path / "poetry.lock").unlink()
    (tmp_path / "package-lock.json").touch()
    assert detector.detect(tmp_path) == "npm"

def test_dependency_detector_package_json(tmp_path):
    pkg_json = {
        "dependencies": {"react": "^18.0.0", "next": "12.0.0"},
        "devDependencies": {"jest": "27.0.0"}
    }
    (tmp_path / "package.json").write_text(json.dumps(pkg_json))
    
    detector = DependencyDetector()
    files, deps = detector.detect(tmp_path)
    assert "package.json" in files
    assert sorted(["react", "next", "jest"]) == deps

def test_dependency_detector_requirements_txt(tmp_path):
    (tmp_path / "requirements.txt").write_text("fastapi==0.95.0\npydantic>=1.10.0\n# comment\npytest")
    
    detector = DependencyDetector()
    files, deps = detector.detect(tmp_path)
    assert "requirements.txt" in files
    assert sorted(["fastapi", "pydantic", "pytest"]) == deps

def test_dependency_detector_malformed(tmp_path):
    (tmp_path / "package.json").write_text("invalid json {")
    detector = DependencyDetector()
    # Should not crash, graceful failure
    files, deps = detector.detect(tmp_path)
    assert "package.json" in files
    assert deps == []
