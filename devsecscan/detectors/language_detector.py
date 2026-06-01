from pathlib import Path

class LanguageDetector:
    EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".php": "php"
    }

    def detect(self, path: Path) -> dict[str, float]:
        """
        Detects languages based on file extensions.
        Returns a dictionary of language -> confidence score (0.0 to 1.0).
        """
        if not path.exists() or not path.is_dir():
            return {}

        counts = {lang: 0 for lang in self.EXTENSIONS.values()}
        total_files = 0
        
        # Traverse the directory tree without loading files into memory
        for file_path in path.rglob("*"):
            if file_path.is_file():
                # Basic exclusion for common non-source directories
                parts = file_path.parts
                if any(ignored in parts for ignored in (".git", "node_modules", "venv", "__pycache__", ".venv", "target", "build", "dist")):
                    continue
                    
                total_files += 1
                ext = file_path.suffix.lower()
                if ext in self.EXTENSIONS:
                    lang = self.EXTENSIONS[ext]
                    counts[lang] += 1
        
        # If no recognized source files are found, we don't have confidences
        total_recognized = sum(counts.values())
        if total_recognized == 0:
            return {}
            
        # Calculate scores
        scores = {}
        for lang, count in counts.items():
            if count > 0:
                scores[lang] = round(count / total_recognized, 2)
                
        # Sort by confidence descending
        return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

    def get_primary_language(self, scores: dict[str, float]) -> str | None:
        """Returns the language with the highest confidence score."""
        if not scores:
            return None
        return next(iter(scores.keys()))
