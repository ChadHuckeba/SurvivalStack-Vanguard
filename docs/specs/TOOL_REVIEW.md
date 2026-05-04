# VANGUARD: THIRD-PARTY TOOL REVIEW

## 1.0 CANDIDATE ADAPTER: JOBSPY
*   **Status**: SELECTED (Alpha Phase)
*   **Rationale**: Open-source, Python-native, and requires no API keys for initial scraping. It aggregates LinkedIn, Indeed, and ZipRecruiter into a unified DataFrame.
*   **Limitations**: Subject to IP-based rate limiting; requires robust error handling for "Scraping Blocked" events (429 errors).
*   **Implementation**: Utilized by `JobSearchScout`.

## 2.0 CANDIDATE ADAPTER: PROXY/ROTATION SERVICES
*   **Status**: EVALUATED / DEFERRED (Phase 2)
*   **Rationale**: While necessary for high-volume scraping, these incur costs that violate the **Bootstrap-First** mandate of the Alpha phase. 
*   **Strategy**: Re-evaluate during the Intelligence/Beta phase if market noise requires higher acquisition volumes.

## 3.0 ALIGNMENT ENGINE: GEMINI 2.5 FLASH
*   **Status**: SELECTED
*   **Rationale**: High token window allows for processing massive job descriptions against a comprehensive career history. Fast inference and cost-effective for "Semantic Alignment" (Semantic Gap Analysis) tasks.
*   **Constraint**: Must be accessed via free-tier or local-first methods to maintain **Bootstrap-First** compliance.
