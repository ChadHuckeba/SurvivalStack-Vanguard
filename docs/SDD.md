# VANGUARD: SYSTEM DESIGN DOCUMENT (TACTICAL)

## 1.0 SYSTEM ARCHITECTURE
Vanguard utilizes a Hub-and-Spoke architecture written in Python 3.12+. The ScoutCore acts as the hub (orchestrator) and modular Scouts act as spokes (probes).
* **PEP 257**: Every class and function must include a descriptive docstring.
* **PEP 484**: Mandatory Type Hinting for all signatures to ensure self-documentation.
* **Traceability**: Complex logic must reference VAN_SDD or VAN_CORE_LOGIC in code comments.

## 2.0 CORE COMPONENTS
* **ScoutCore**: A singleton class for configuration, registration, and persistence.
* **Scouts**: Classes inheriting from a `BaseScout` template.
    ### 2.1 Contract Compliance
    All component communication and internal data structures must strictly adhere to the standards defined in _VAN_CONTRACT_DEFINITIONS. The ScoutCore persistence layer must utilize the VAN_PERSISTENCE_INTERFACE to ensure an 'Alpha-to-Beta' migration path (JSON to SQLite) without altering core logic.

## 3.0 DATA STORAGE & ATOMIC WRITE PROTOCOL
* **Alpha Persistence**: Single-file `state.json`.
* **Safe-Swap Routine**: 
    1. Rename `state.json` to `state.json.bak`.
    2. Write new data to `state.tmp`.
    3. Rename `state.tmp` to `state.json` upon success.
* **Deduplication**: SHA-256 hash of [Sanitized_Base_URL] + [Entity_Title]. 
    
    Deduplication logic and unique ID generation (SHA-256) are governed by the Discovery Contract. Direct file-system manipulation is prohibited; all I/O must pass through the Interface Contract DAO methods.

## 4.0 MODULAR SEPARATION
* **Scouts (Gatherers)**: Perform external network requests.
* **Processors (Sifters)**: Perform internal logic/cleaning on existing data.
* **Logic Rule**: Features not requiring new external connections must be Processors, not Scouts.

## 5.0 EXTERNAL INTEGRATIONS & SECURITY
* **JobSpy**: Translates DataFrame output to the Vanguard JSON Contract.
* **PII Encryption**: Local profiles must be encrypted at rest using Fernet; keys are isolated in `.env`.
* **Jitter Protocol**: Randomized delays of 15–45 seconds between requests.
* **Exponential Backoff**: Minimum 4-hour session termination upon 429 errors.
