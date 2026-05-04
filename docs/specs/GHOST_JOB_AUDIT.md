# VANGUARD: RESEARCH - GHOST JOB AUDIT

## 1.0 OBJECTIVE
To identify and categorize the primary indicators of "Ghost Jobs"—listings that are inactive, stale, or posted without immediate hiring intent—to inform the Multi-Vector Data Validation (MVDV) logic.

## 2.0 IDENTIFIED GHOST JOB SIGNALS
The following signals have been identified as high-probability indicators of market noise and "Ghost Jobs":
*   **High Repost Frequency**: Listings that are automatically reposted every 30 days without changes to the unique job ID or description.
*   **Metadata Decay**: Cases where the "Date Posted" is significantly older than the "Date Modified" in the aggregator's API.
*   **Domain Discrepancy**: Listings on third-party aggregators (e.g., LinkedIn, Indeed) that do not exist on the hiring company's official "Careers" portal.
*   **Generic Requirements**: Overly broad role descriptions often used for "Resume Harvesting" rather than specific head-count fulfillment.

## 3.0 MARKET IMPACT
Research indicates that up to 30-40% of tech listings on major aggregators in 2026 exhibit one or more of these signals, leading to high "Applicant Friction" and wasted resources.

## 4.0 MVDV INTEGRATION REQUIREMENTS
The Vanguard MVDV logic (as defined in `PROPRIETARY_LOGIC.md`) must account for these signals:
*   **Domain Verification**: Assign a significant integrity penalty where the company domain cannot be verified.
*   **Hit Count Analysis**: Flag entries appearing in more than three consecutive 30-day scrape cycles.
