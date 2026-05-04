# VANGUARD: FUNCTIONAL SPECIFICATION DOCUMENT (TACTICAL)

## 1. INTRODUCTION
This document defines the functional requirements for the Vanguard platform, specifically the ScoutCore engine and the initial JobScout module. 

### 1.1 IMPLEMENTATION AUTHORITY
This repository serves as the high-authority source of truth for all Vanguard functional requirements and technical designs. Technical decisions must align with the documentation housed in `/docs`.

## 2. SYSTEM OVERVIEW
Vanguard is a modular, agentic system composed of a central orchestration engine (ScoutCore) and domain-specific data probes (Scouts). The system utilizes a "pull" architecture to retrieve, validate, and store data leads.

## 3. SCOUTCORE ENGINE REQUIREMENTS
* **Execution Orchestration**: The Core must initialize, execute, and terminate Scout modules.
* **State Management**: Maintain a persistent local record in `state.json`.
* **Deduplication**: Prevent ingestion of duplicate leads using unique `vanguard_id` hashes.
* **URL Sanitization**: Strip query parameters and fragments before hashing to prevent collisions.
* **Error Handling**: Log failures without terminating the system process.

## 4. JOBSCOUT REQUIREMENTS
* **Data Acquisition**: Utilize the JobSpy adapter for aggregator retrieval.
* **Lead Integrity**: Apply Multi-Vector Data Validation (MVDV) to identify "Ghost Jobs".
* **Semantic Alignment**: Perform match analysis against the user’s career profile.
* **Standardized Output**: Adhere strictly to the VAN_CONTRACT_DISCOVERY.

## 5. STATE TRANSITION & LIFECYCLE
* **Mandatory States**: New, Reviewed, Applied, Rejected, Expired, and Failed.
* **Failed State**: Reserved for critical errors during retrieval or MVDV logic.
* **State Decay**: Leads older than 30 days automatically transition to Expired.
* **Integrity Trigger**: Leads falling below the system integrity threshold during re-scan are marked Expired.

## 6. INTERFACE & SECURITY
* **CLI**: Alpha phase focuses on manual execution via command line.
* **Data Privacy**: No PII beyond the user profile shall be transmitted to external adapters.
* **Rate Limiting**: Implement randomized Jitter and mandatory cooldowns after scraping blocks.
