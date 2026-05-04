# VANGUARD: PROJECT INDEX & OPERATIONAL MANUAL

## 1.0 PROJECT IDENTITY
*   **Organization**: SurvivalStack
*   **Product**: Vanguard
*   **Engine (The Chassis)**: `ScoutCore` is the foundational service layer providing state persistence, MVDV integrity scoring, and Entry lifecycle management. It is domain-agnostic and serves as the "System of Record".
*   **Agents (The Probes)**: `Scouts` are domain-specific data probes (e.g., `JobSearchScout`).

## 2.0 LOCATIONAL AUTHORITY
**Supreme Directive**: This repository is the high-authority source of truth for the Vanguard project. Any technical discrepancy between external mirrors (e.g., Google Drive) and GitHub is resolved in favor of the GitHub `/docs` and `/src` directories.

### 2.1 Documentation Hierarchy
| Document | Authority Level | Location | Scope |
| :--- | :--- | :--- | :--- |
| **VAN_GLOSSARY** | Layer 1 (Global) | `/docs/GLOSSARY.md` | Standardized terminology and logic definitions. |
| **VAN_CHARTER** | Layer 1 (Global) | `/docs/specs/PROJECT_CHARTER.md` | Executive vision, scope gates, and zero-cost mandates. |
| **VAN_PAEP** | Layer 2 (Project) | `/docs/PAEP.md` | Project-specific personas, heuristics, and bylaws. |
| **VAN_INDEX** | Layer 2 (Project) | `/docs/PROJECT_INDEX.md` | This manual; master directory and authority map. |
| **VAN_FSD** | Layer 2 (Tactical) | `/docs/specs/FUNCTIONAL_SPEC.md` | Functional requirements and lead lifecycle logic. |
| **VAN_SDD** | Layer 2 (Tactical) | `/docs/specs/TECHNICAL_DESIGN.md` | System architecture, flow diagrams, and security protocols. |
| **VAN_LOGIC** | Layer 2 (Proprietary) | `/docs/specs/PROPRIETARY_LOGIC.md` | MVDV and Semantic Alignment methodologies (Abstracted). |
| **VAN_CONTRACTS** | Layer 2 (Technical) | `/docs/contracts/` | Data handshakes (Discovery, Persistence, Interface). |
| **Source Code** | Layer 3 (Operational) | `/src/` | Executable Python 3.12+ modules and persistence interfaces. |

## 3.0 OPERATIONAL STANDARDS

### 3.1 Naming Conventions
*   **Documentation**: High-authority specifications must retain the `VAN_` prefix in descriptions but use `UPPERCASE_SNAKE_CASE` for filenames (e.g., `VAN_SDD.md`).
*   **Code**: Implementation files must use `lowercase_snake_case` and exclude the `VAN_` prefix (e.g., `scout_core.py`) to ensure PEP 8 compliance.

### 3.2 AI Operational Instructions (The Audit Protocol)
*   **Primary Authority**: AI must prioritize `/docs/specs/` and `/docs/contracts/` for logic.
*   **Logic Isolation**: Mathematical weights and MVDV heuristics must remain isolated in `.env` or internal-only files. AI must use abstract placeholders in documentation.
*   **No Assumption Policy**: If a requirement is not explicitly defined in the `VAN_` corpus, the AI must flag it as "Undefined" and seek user clarification.
*   **Documentation Impact Assessment (DIA)**: Every significant technical decision or session must conclude with a DIA section identifying affected documents and their authority levels.

## 4.0 DESIGN TENETS
*   **Bootstrap-First Infrastructure**: Prioritize zero-cost, local, or free-tier resources for the Alpha phase.
*   **Agentic Readiness**: All module outputs must adhere to the `VAN_CONTRACT_DISCOVERY` to facilitate autonomous interaction.
*   **Modular Decoupling**: The engine (`ScoutCore`) must remain agnostic of the specific implementation of its Scouts.

## 5.0 IP PROTECTION & SECURITY
*   **Functional Abstraction**: Public/Shared documentation must define Inputs and Outputs only.
*   **Credential Isolation**: API keys, tokens, and logic thresholds must never be committed to version control. Use `.env` exclusively.
*   **Context Sanitization**: Ensure proprietary identifiers are redacted before sharing context with external/non-enterprise AI environments.
