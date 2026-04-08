# Vanguard

Vanguard is a modular, agentic orchestration engine designed for high-fidelity lead retrieval, validation, and state management.

## 🏗️ Architecture
Vanguard operates on a "Hub-and-Spoke" model:
* **ScoutCore**: The central engine responsible for lifecycle management, jitter, and state persistence.
* **Scouts**: Modular, domain-specific adapters used for data acquisition (e.g., JobScout).

## 📂 Project Structure
* `/docs`: Technical specifications and functional baselines (Tactical Layer).
* `/src`: Core implementation logic and persistence interfaces (Operational Layer).
* `/tests`: Validation suites for engine and scout integrity.

## 🛠️ Tech Stack
* **Language**: Python 3.12+
* **Framework**: Modular Engine-Scout Architecture
* **Standards**: SemVer 0.x.y, Conventional Commits, PEP 8 Compliance

---
*Note: This repository houses the Tactical and Operational layers of the Vanguard project. Internal strategic documentation is maintained privately.*