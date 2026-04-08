# VANGUARD: SYSTEM DESIGN DOCUMENT (TACTICAL)

## 1. SYSTEM ARCHITECTURE
[cite_start]Vanguard utilizes a Hub-and-Spoke architecture written in Python 3.12+[cite: 157]. [cite_start]The ScoutCore acts as the hub (orchestrator) and modular Scouts act as spokes (probes)[cite: 158].

### 1.1 INLINE-FIRST DOCUMENTATION
* [cite_start]**PEP 257**: Every class and function must include a descriptive docstring[cite: 161].
* [cite_start]**PEP 484**: Mandatory Type Hinting for all signatures to ensure self-documentation[cite: 162].
* [cite_start]**Traceability**: Complex logic must reference VAN_SDD or VAN_CORE_LOGIC in code comments[cite: 163].

## 2. CORE COMPONENTS
* [cite_start]**ScoutCore**: A singleton class for configuration, registration, and persistence[cite: 164].
* [cite_start]**Scouts**: Classes inheriting from a `BaseScout` template[cite: 165].

## 3. DATA STORAGE & ATOMIC WRITE PROTOCOL
* [cite_start]**Alpha Persistence**: Single-file `state.json`[cite: 166].
* **Safe-Swap Routine**: 
    1. [cite_start]Rename `state.json` to `state.json.bak`[cite: 170].
    2. [cite_start]Write new data to `state.tmp`[cite: 170].
    3. [cite_start]Rename `state.tmp` to `state.json` upon success[cite: 171].
* [cite_start]**Deduplication**: SHA-256 hash of [Sanitized_Base_URL] + [Entity_Title][cite: 173, 176].

## 4. MODULAR SEPARATION
* [cite_start]**Scouts (Gatherers)**: Perform external network requests[cite: 178].
* [cite_start]**Processors (Sifters)**: Perform internal logic/cleaning on existing data[cite: 179].
* [cite_start]**Logic Rule**: Features not requiring new external connections must be Processors, not Scouts[cite: 180].

## 5. EXTERNAL INTEGRATIONS & SECURITY
* [cite_start]**JobSpy**: Translates DataFrame output to the Vanguard JSON Contract[cite: 187].
* [cite_start]**PII Encryption**: Local profiles must be encrypted at rest using Fernet; keys are isolated in `.env`[cite: 189, 190].
* [cite_start]**Jitter Protocol**: Randomized delays of 15–45 seconds between requests[cite: 193].
* [cite_start]**Exponential Backoff**: Minimum 4-hour session termination upon 429 errors[cite: 195].