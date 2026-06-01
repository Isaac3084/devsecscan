from pathlib import Path

class FrameworkDetector:
    FRAMEWORK_MAPPINGS = {
        "fastapi": "fastapi",
        "flask": "flask",
        "django": "django",
        "react": "react",
        "next": "next.js",
        "express": "express",
        "@nestjs/core": "nestjs",
        "vue": "vue"
    }

    def detect(self, dependencies: list[str]) -> str | None:
        """
        Detects the primary framework used based on extracted dependencies.
        Returns the framework name, or None if unknown.
        """
        # Convert dependencies to lowercase for easier matching
        deps_lower = {d.lower() for d in dependencies}
        
        # We check specific frameworks first (e.g. next.js builds on react, so check next first if needed, 
        # though the keys here are unique enough)
        
        if "next" in deps_lower:
            return "next.js"
        if "@nestjs/core" in deps_lower or "@nestjs/common" in deps_lower:
            return "nestjs"
            
        for dep, framework in self.FRAMEWORK_MAPPINGS.items():
            if dep in deps_lower:
                return framework
                
        return None
