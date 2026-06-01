import os
from pathlib import Path
from ..interfaces.analyzer import BaseAnalyzer
from ..models.domain import RepositoryContext, RepositoryAnalysisError
from ..detectors import LanguageDetector, DependencyDetector, PackageManagerDetector, FrameworkDetector
from ..repository.scan_planner import ScanPlanner

class RepositoryAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.dependency_detector = DependencyDetector()
        self.package_manager_detector = PackageManagerDetector()
        self.framework_detector = FrameworkDetector()
        self.scan_planner = ScanPlanner()

    def analyze(self, path: str) -> RepositoryContext:
        """
        Analyzes a repository and extracts its context.
        Raises RepositoryAnalysisError if the path is invalid.
        """
        p = Path(path)
        if not p.exists() or not p.is_dir():
            raise RepositoryAnalysisError(f"Repository path does not exist or is not a directory: {path}")

        # Basic context
        project_name = p.name if p.name else "unknown"
        
        # 1. Detect Languages
        detected_languages = self.language_detector.detect(p)
        primary_language = self.language_detector.get_primary_language(detected_languages)
        
        # We can calculate total_files during language detection, but if there's no code,
        # we still want to count files. For now, since language_detector filters non-code,
        # we'll do a quick scan for total files here or just rely on the detector if we update it.
        # Let's count total_files safely.
        total_files = sum(1 for _ in p.rglob("*") if _.is_file() and not any(ignored in _.parts for ignored in (".git", "node_modules", "venv", "__pycache__")))

        # 2. Detect Package Manager
        package_manager = self.package_manager_detector.detect(p)

        # 3. Detect Dependencies
        dependency_files, dependencies = self.dependency_detector.detect(p)

        # 4. Detect Framework
        framework = self.framework_detector.detect(dependencies)

        # 5. Generate scan plan before any security detector runs
        scan_plan = self.scan_planner.plan(p)
        
        # 6. Determine source directories from the scan plan
        source_directories = list(scan_plan.scan_directories)

        return RepositoryContext(
            project_name=project_name,
            project_path=str(p.absolute()),
            primary_language=primary_language,
            detected_languages=detected_languages,
            framework=framework,
            package_manager=package_manager,
            dependency_files=dependency_files,
            dependencies=dependencies,
            total_files=total_files,
            source_directories=source_directories,
            scan_plan=scan_plan,
        )
