# VANGUARD: FUNCTIONAL SPECIFICATION DOCUMENT (TACTICAL)

## 1. INTRODUCTION
[cite_start]This document defines the functional requirements for the Vanguard platform, specifically the ScoutCore engine and the initial JobScout module[cite: 113]. 

### 1.1 IMPLEMENTATION STANDARD
[cite_start]While this document serves as the tactical representation for development and testing, the high-authority logic is governed by the Google Doc VAN_FSD[cite: 115]. [cite_start]Discrepancies are resolved in favor of the Google Doc unless a 'Sync' trigger has officially promoted this version[cite: 115].

## 2. SYSTEM OVERVIEW
[cite_start]Vanguard is a modular, agentic system composed of a central orchestration engine (ScoutCore) and domain-specific data probes (Scouts)[cite: 115]. [cite_start]The system utilizes a "pull" architecture to retrieve, validate, and store data leads[cite: 115].

## 3. SCOUTCORE ENGINE REQUIREMENTS
* [cite_start]**Execution Orchestration**: The Core must initialize, execute, and terminate Scout modules[cite: 116].
* [cite_start]**State Management**: Maintain a persistent local record in `state.json`[cite: 117].
* [cite_start]**Deduplication**: Prevent ingestion of duplicate leads using unique `vanguard_id` hashes[cite: 118].
* [cite_start]**URL Sanitization**: Strip query parameters and fragments before hashing to prevent collisions[cite: 118].
* [cite_start]**Error Handling**: Log failures without terminating the system process[cite: 119].

## 4. JOBSCOUT REQUIREMENTS
* [cite_start]**Data Acquisition**: Utilize the JobSpy adapter for aggregator retrieval[cite: 120].
* [cite_start]**Lead Integrity**: Apply Multi-Vector Data Validation (MVDV) to identify "Ghost Jobs"[cite: 121].
* [cite_start]**Semantic Alignment**: Perform match analysis against the user’s career profile[cite: 122].
* [cite_start]**Standardized Output**: Adhere strictly to the VAN_Scout_JSON_Contract[cite: 123].

## 5. STATE TRANSITION & LIFECYCLE
* [cite_start]**Mandatory States**: New, Reviewed, Applied, Rejected, Expired, and Failed[cite: 124].
* [cite_start]**Failed State**: Reserved for critical errors during retrieval or MVDV logic[cite: 125].
* [cite_start]**State Decay**: Leads older than 30 days automatically transition to Expired[cite: 126].
* [cite_start]**Integrity Trigger**: Leads falling below the system integrity threshold during re-scan are marked Expired[cite: 127].

## 6. INTERFACE & SECURITY
* [cite_start]**CLI**: Alpha phase focuses on manual execution via command line[cite: 128].
* [cite_start]**Data Privacy**: No PII beyond the user profile shall be transmitted to external adapters[cite: 129].
* [cite_start]**Rate Limiting**: Implement randomized Jitter and mandatory cooldowns after scraping blocks[cite: 130].