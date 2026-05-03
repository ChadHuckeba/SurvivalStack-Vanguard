# VANGUARD: SYSTEM DESIGN DOCUMENT

## 1.0 SYSTEM ARCHITECTURE
Vanguard utilizes a Hub-and-Spoke architecture written in Python 3.12+. The ScoutCore acts as the hub (orchestrator) and modular Scouts act as spokes (probes).
* **PEP 257**: Every class and function must include a descriptive docstring.
* **PEP 484**: Mandatory Type Hinting for all signatures to ensure self-documentation.
* **Traceability**: Complex logic must reference VAN_SDD or VAN_CORE_LOGIC in code comments.

## 2.0 PRODUCT ROADMAP

### Phase 1: Foundation (Alpha)
*Focus: Infrastructure and Data Acquisition.*
* **1.1 ScoutCore Development**: Finalize execution chassis and state management logic.
* **1.2 JobSpy Integration**: Implement `JobSearchScout` using the JobSpy adapter.
* **1.3 Basic Heuristics**: Implement Multi-Vector Data Validation (MVDV) to filter market noise.
* **1.4 Documentation Authority**: Finalize FSD, SDD, and Data Contracts within this repository.

### Phase 2: Intelligence (Beta)
*Focus: Proprietary Logic and Signal Integration.*
* **2.1 Custom Scouts**: Migrate to native, proprietary scraping modules.
* **2.2 Semantic Gap Analysis**: Compare user profile data against lead requirements.
* **2.3 Signal-to-Search**: Event-Driven Orchestration based on market catalysts (funding, news).
* **2.4 Persistence Migration**: Complete migration from `state.json` to SQLite for scalable querying.

### Phase 3: Autonomy (Production)
*Focus: Agentic Workflow and Scale.*
* **3.1 LLM Triage Layer**: Autonomous triage using LLMs to rank and summarize leads.
* **3.2 Automated Outreach**: (Optional) Draft introductory signals based on lead data.
* **3.3 Multi-Domain Expansion**: Deploy Scouts for market research and service leads.

## 3.0 CORE COMPONENTS
* **ScoutCore**: A singleton class for configuration, registration, and persistence.
* **Scouts**: Classes inheriting from a `BaseScout` template.
    ### 3.1 Contract Compliance
    All component communication and internal data structures must strictly adhere to the standards defined in _VAN_CONTRACT_MASTER. The ScoutCore persistence layer must utilize the VAN_CONTRACT_INTERFACE to ensure an 'Alpha-to-Beta' migration path (JSON to SQLite) without altering core logic.

## 4.0 DATA STORAGE & ATOMIC WRITE PROTOCOL
* **Alpha Persistence**: Single-file `state.json`.
* **Beta Persistence**: SQLite Database (`vanguard.db`) using WAL mode.
* **Safe-Swap Routine (Legacy)**: 
    1. Rename `state.json` to `state.json.bak`.
    2. Write new data to `state.tmp`.
    3. Rename `state.tmp` to `state.json` upon success.
* **Deduplication**: SHA-256 hash of [Sanitized_Base_URL] + [Entity_Title]. 
    1. Deduplication logic and unique ID generation (SHA-256) are governed by the VAN_CONTRACT_DISCOVERY. Direct file-system manipulation is prohibited; all I/O must pass through the VAN_CONTRACT_INTERFACE DAO methods.

## 5.0 MODULAR SEPARATION
* **Scouts (Gatherers)**: Perform external network requests.
* **Processors (Sifters)**: Perform internal logic/cleaning on existing data.
* **Logic Rule**: Features not requiring new external connections must be Processors, not Scouts.

## 6.0 EXTERNAL INTEGRATIONS & SECURITY
* **JobSpy**: Translates DataFrame output to the Vanguard JSON Contract.
* **PII Encryption**: Local profiles must be encrypted at rest using Fernet; keys are isolated in `.env`.
* **Jitter Protocol**: Randomized delays of 15–45 seconds between requests.
* **Exponential Backoff**: Minimum 4-hour session termination upon 429 errors.
