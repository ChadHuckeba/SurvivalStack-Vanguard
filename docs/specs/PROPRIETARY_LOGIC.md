# VANGUARD: PROPRIETARY LOGIC FRAMEWORK

## 1.0 IP PROTECTION AND DATA SOVEREIGNTY
In accordance with the Vanguard Project Charter, this document defines the functional methodology for high-fidelity data validation. 
*   **Functional Abstraction**: This specification defines inputs, outputs, and logical vectors. Specific numerical weights and threshold constants must remain isolated in environment variables.
*   **Credential Isolation**: Logic thresholds and proprietary weights must never be hardcoded or committed to version control.

## 2.0 MVDV: MULTI-VECTOR DATA VALIDATION
Heuristics used to calculate the **Integrity Score** (0.0 to 1.0) to identify "Ghost Jobs" and stale listings.

### A. Age Vector (V_age)
*   **Logic**: Proximity of "Date Posted" to current system time.
*   **Formula Strategy**: Linear decay model. 
    *   Full integrity (1.0) for entries within the `MVDV_AGE_PRIME` window.
    *   Linear degradation between `MVDV_AGE_PRIME` and `MVDV_AGE_MAX`.
    *   Zero integrity (0.0) beyond `MVDV_AGE_MAX`, triggering a baseline ghost probability penalty.

### B. Frequency Vector (V_freq)
*   **Logic**: Monitoring discovery frequency across consecutive scrape cycles.
*   **Constraint**: High-frequency recurrence of the same `vanguard_id` (hit count) within a defined cycle window triggers a multiplier penalty to the total Integrity Score.

### C. Metadata Vector (V_meta)
*   **Logic**: Domain verification and structural analysis.
*   **Penalties**:
    *   **Domain Mismatch**: Penalty applied if the entry source cannot be verified against the hiring company's official domain.
    *   **Templated Content**: Penalty applied for generic, low-signal descriptions.

### D. Composite Integrity Score
*   **Calculation**: Weighted average of `V_age`, `V_freq`, and `V_meta`.
*   **Automation Trigger**: If the Composite Score falls below `MVDV_INTEGRITY_THRESHOLD`, the entry is marked as `is_ghost_job = TRUE` and the status is set to `expired`.

## 3.0 SEMANTIC ALIGNMENT LOGIC
Methodology for high-fidelity gap analysis between user career profiles and discovery entries.

### A. Core Requirement Extraction
*   **Process**: Entity Extraction focusing on "Hard Skills" and "Domain Expertise" requirements.

### B. Experience Delta
*   **Logic**: Comparison of candidate years of experience against lead requirements.
*   **Constraint**: Score caps at 1.0; values below the `SEMANTIC_SENIORITY_MIN` threshold trigger a "Seniority Gap" flag.

### C. Alignment Score
*   **Calculation**: Aggregated match rate of Skills, Experience Delta, and Seniority alignment.

## 4.0 SYSTEM THRESHOLDS (CONFIG)
The following parameters must be configured via `.env` to execute the logic defined above:
*   `MVDV_AGE_PRIME`: Days of "Prime" integrity.
*   `MVDV_AGE_MAX`: Maximum age before zeroing integrity.
*   `MVDV_INTEGRITY_THRESHOLD`: Score below which a lead is considered a "Ghost".
*   `SEMANTIC_SENIORITY_MIN`: Minimum experience ratio before flagging.
*   `STATE_DECAY_DAYS`: TTL for active entries.
