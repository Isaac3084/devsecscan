# DevSecScan

DevSecScan is a local, deterministic repository security scanner. Phase 6 adds a rule-based risk classification engine that turns technical findings into business risk assessments and deployment recommendations.

## Updated Architecture Diagram

```mermaid
flowchart TD
    Repository["Repository"] --> Analyzer["Repository Analyzer"]
    Analyzer --> Context["RepositoryContext"]
    Context --> Detectors["Security Detectors"]
    Detectors --> FindingEngine["Finding Engine"]
    FindingEngine --> Findings["Findings"]
    Findings --> RiskClassifier["Risk Classification Engine"]
    RiskClassifier --> RiskAssessments["Risk Assessments"]
    Findings --> DeploymentGate["Deployment Gate"]
    RiskAssessments --> DeploymentGate
    DeploymentGate --> Summary["RepositoryRiskSummary"]
    Summary --> Formatter["CLI Preview Output"]
    RiskAssessments --> FutureAI["Future AI Layer"]
```

## Class Diagram

```mermaid
classDiagram
    class RepositoryAnalyzer {
        +analyze(path) RepositoryContext
    }
    class FindingEngine {
        +register(detector)
        +run(context) list~Finding~
    }
    class SecretDetector {
        +detect(context) list~Finding~
    }
    class RiskClassifier {
        +classify(finding) RiskAssessment
        +classify_all(findings) list~RiskAssessment~
    }
    class RiskRegistry {
        +lookup(category, severity) RiskMapping
    }
    class RecommendationEngine {
        +recommend(category) str
    }
    class DeploymentGate {
        +evaluate(findings, assessments) RepositoryRiskSummary
    }
    class RiskAssessment {
        +finding_id str
        +risk_type str
        +likelihood str
        +impact str
        +business_consequence str
        +recommendation str
        +deployment_status DeploymentStatus
        +confidence float
    }
    class RepositoryRiskSummary {
        +total_findings int
        +critical int
        +high int
        +medium int
        +low int
        +info int
        +deployment_status DeploymentStatus
        +assessments list~RiskAssessment~
    }

    RepositoryAnalyzer --> FindingEngine
    FindingEngine --> SecretDetector
    RiskClassifier --> RiskRegistry
    RiskClassifier --> RecommendationEngine
    RiskClassifier --> RiskAssessment
    DeploymentGate --> RepositoryRiskSummary
```

## Data Flow Diagram

```mermaid
flowchart LR
    SourceFiles["Source Files"] --> IgnoreSystem["Ignore System"]
    IgnoreSystem --> FileScanner["FileScanner"]
    FileScanner --> SecretRules["Secret Rules"]
    SecretRules --> Findings["Normalized Findings"]
    Findings --> Registry["Risk Registry"]
    Registry --> Assessments["Risk Assessments"]
    Assessments --> Gate["Deployment Gate"]
    Gate --> Output["Repository Risk Summary"]
```

## Implementation Plan

1. Keep risk mapping local and rule-based.
2. Normalize detector output through `Finding`.
3. Map `(Category, Severity)` pairs through `RiskRegistry`.
4. Generate human-readable remediation through `RecommendationEngine`.
5. Aggregate final repository safety through `DeploymentGate`.
6. Render terminal preview output from `RepositoryRiskSummary`.
7. Preserve ignore support so test fixtures and generated folders do not create findings.
8. Add tests for models, classification, recommendations, gate behavior, ignored paths, summary formatting, and CLI preview output.

## Usage

```powershell
devsecscan .
```

or from source:

```powershell
python -m devsecscan.cli.main .
```

Example output:

```text
Repository Risk Summary

Total Findings: 2
Critical Issues: 1
High Issues: 1
Medium Issues: 0
Low Issues: 0
Info Issues: 0

Deployment Recommendation:
DO_NOT_DEPLOY

Top Risks:
1. Credential Exposure
2. Unauthorized Access
```

## Risk Engine

The risk engine is offline only. It does not call AI providers, cloud APIs, or external services. Future detectors can add new categories or severities by extending the registry mapping without changing the classifier core.

## Ignore System

DevSecScan ignores common generated and fixture paths by default:

```text
tests/
node_modules/
.git/
coverage/
dist/
build/
__pycache__/
.venv/
venv/
```

Add project-specific ignores in `.devsecscanignore`.

## Tests

```powershell
pytest -q
```
