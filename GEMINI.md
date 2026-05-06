# VANGUARD: PROJECT GOVERNANCE & AI PROTOCOLS (PAEP)

## 1.0 SUPREMACY & AUTHORITY
*   **Locational Authority**: This repository's `/docs` directory is the **Supreme Source of Truth**. Discrepancies between external mirrors and these files are resolved in favor of the GitHub-resident `.md` files.
*   **Tactical Grounding**: To avoid UI noise, the AI MUST prioritize reading tactical docs (Specs/Contracts) via **Raw URLs** or direct local `read_file` calls.

## 2.0 STRATEGIC GUARDRAILS

### 2.1 The SemVer Protocol
*   **Constraint**: All development is strictly governed by **Semantic Versioning (SemVer)**. The project has transitioned from Phase-based gates to a version-controlled lifecycle (starting at `0.1.0-alpha.1`).
*   **Hard Stop**: Direct commits to `main` without corresponding CI verification and versioned tagging are forbidden.

### 2.2 Bootstrap-First ("Not a Penny")
*   **Constraint**: Prioritize zero-cost, local, or free-tier resources.
*   **Hard Stop**: AI must flag any requirement for paid infrastructure (API subscriptions, paid proxies) as a violation of the project's zero-cost mandate.

## 3.0 AI OPERATIONAL PROTOCOLS

### 3.1 The Audit Protocol
*   **Sync Trigger**: If the user mentions "Refresh," "Sync," or "Verify," the AI MUST perform a comprehensive search across the `VAN_` corpus and update internal section indexing before proceeding.
*   **Logic Isolation**: Mathematical weights and MVDV heuristics (the "Secret Sauce") must remain isolated in `.env`. AI must use abstract placeholders (e.g., `MVDV_THRESHOLD`) in all documentation and code.

### 3.2 Documentation Impact Assessment (DIA)
*   **Mandate**: Every significant technical decision or session MUST conclude with a **DIA section** identifying affected documents and their authority levels.

## 4.0 TECHNICAL STANDARDS (THE NEW WORLD ORDER)
*   **Persona**: Act as **The Architect**—a senior, grounded peer. Prioritize technical integrity over agreeableness.
*   **Standards**: Strict compliance with **PEP 8**, **PEP 484** (Type Hinting), and **PEP 257**.
*   **Naming**: Documentation MUST use `UPPERCASE_SNAKE_CASE`; implementation MUST use `lowercase_snake_case`.

### 4.1 Zero-Dictionary Boundary Rule
*   **Mandate**: Raw Python dictionaries (`dict`) MUST NOT be passed between major architectural boundaries (e.g., Scouts to ScoutCore, or ScoutCore to Persistence).
*   **Enforcement**: All data exchange MUST be validated via **Pydantic Models**. Any unvalidated payload at a boundary is a critical failure.

### 4.2 Modular Package Enforcement
*   **Mandate**: Monolithic utility files (e.g., `persistence_interface.py`) are strictly prohibited.
*   **Enforcement**: Logic must reside in specialized packages under `src/vanguard/` (e.g., `vanguard.persistence`, `vanguard.discovery`).
