# VANGUARD: GLOBAL GLOSSARY

## 📜 GLOSSARY HIERARCHY & INHERITANCE
This is a **Layer 2 (Project)** glossary. It inherits all universal terms defined in the **CORE_GLOSSARY**.
*   **Universal Definitions**: For global business and AI engagement terms (e.g., GAEP, PAEP), refer to the CORE_GLOSSARY.
*   **Project Definitions**: This document contains proprietary terms specific to the Vanguard architecture (e.g., ScoutCore, MVDV).

---

## 🏗️ CORE ARCHITECTURE

### SurvivalStack
The parent organization and philosophy governing the Vanguard project.

### Vanguard
The product name for the modular, automated data acquisition and intelligence platform designed to identify high-fidelity Entries within high-entropy environments. It utilizes a service-oriented architecture to provide standardized validation and persistence for domain-specific Scouts.

### ScoutCore
The foundational service layer (chassis) providing centralized state persistence, MVDV integrity scoring, and Entry lifecycle management. It operates as a domain-agnostic environment that Scouts utilize for standardized data validation and storage. ScoutCore does not contain domain-specific logic but enforces the universal JSON Contract for all incoming data.

### Scout
A specialized, domain-specific agent (probe) designed to identify and retrieve data from a target environment. A Scout is responsible for discovery and initial formatting, utilizing the ScoutCore service layer to process and persist validated Entries via the universal JSON Contract.

---

## 📄 DOCUMENTATION & GOVERNANCE

### PAEP (Project AI Engagement Protocol)
A project-level instructional layer that inherits from the GAEP (Global AI Engagement Protocol). It defines domain-specific logic, proprietary heuristics, and technical standards (e.g., Vanguard's MVDV or Scout architecture). It acts as the "Local Bylaws" for a specific business vertical.

---

## 💾 DATA AND STATE

### Entry
A raw, unverified data point retrieved from a target environment by a Scout. An Entry serves as the primary unit of discovery, such as a URL, job posting, or market signal, before it is processed through the ScoutCore service layer for validation and persistence.

### Result
An Entry that has been successfully processed through the ScoutCore service layer, validated via MVDV logic, and formatted according to the universal JSON Contract. A Result represents the "System of Record" state, ready for persistence and user review.

### State
The persistent memory of the system, currently housed in `vanguard.db` (Beta) or `state.json` (Alpha).

### State Decay
The logic and temporal thresholds used to determine when an Entry is no longer valid, relevant, or active within the system. In the Alpha phase, this is primarily driven by the `last_seen` timestamp, triggering a transition to the **Expired** disposition after a 30-day period of inactivity.

### Discovery Contract (VAN_CONTRACT_DISCOVERY)
The inbound JSON standard for raw data transmission from a Scout to the Core.

### Persistence Schema (VAN_SCHEMA_PERSISTENCE)
The at-rest data structure managed exclusively by the Core for long-term lifecycle tracking.

### Interface Contract (VAN_CONTRACT_INTERFACE)
The functional abstraction (DAO) defining the methods used by the system to interact with storage.

---

## 🎯 DOMAIN SPECIFICS

### Ghost Job
A job listing that is stale, fake, or posted without an active intent to hire; a primary target for MVDV filtering.

### Gap Analysis / Semantic Alignment
The analytical process of identifying the delta between a defined requirement and the specific attributes of an Entry. This process calculates a match percentage based on attributes like hard requirements, domain expertise, and secondary metadata flags.

### Multi-Vector Data Validation (MVDV)
Proprietary heuristics used to verify Entry integrity and filter market noise.

### Vanguard ID
A unique SHA-256 fingerprint generated from an Entry's sanitized source URL and entity title.
