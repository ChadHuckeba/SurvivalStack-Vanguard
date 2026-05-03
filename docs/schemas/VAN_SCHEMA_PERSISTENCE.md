DOCUMENT: VAN_SCHEMA_PERSISTENCE
Status: PRE-PRODUCTION / SPEC-LOCKED
Version: v0.1.0
Authority: ScoutCore Service Layer
Domain: Persistence & State Management
1.0 Implementation Standards
Engine: SQLite 3.x
Mode: Write-Ahead Logging (WAL)
Storage: Local file system (vanguard.db)
Integrity: ACID-compliant transactions for all write operations.

2.0 Table Structures
2.1 Table: entries
The system of record for all data points discovered by Scouts.
Column
Data Type
Constraints
Definition
vanguard_id
TEXT
PRIMARY KEY
SHA-256 hash of the normalized Identity Manifest values.
provider_id
TEXT
NOT NULL
The source of the entry (e.g., 'linkedin', 'syslog').
identity_manifest
TEXT
NOT NULL
JSON array of keys used to generate the hash.
entry_data
TEXT
NOT NULL
JSON blob of raw attributes retrieved by the Scout.
first_seen
DATETIME
DEFAULT CURRENT_TIMESTAMP
Timestamp of initial ingestion.
last_seen
DATETIME
DEFAULT CURRENT_TIMESTAMP
Timestamp of most recent discovery or refresh.
hit_count
INTEGER
DEFAULT 1
Cumulative count of times this entry has been discovered.
status
TEXT
DEFAULT 'active'
Current state: active, expired, or archived.



2.2 Table: enrichment
Stores analysis results from Domain Modules.
Column
Data Type
Constraints
Definition
vanguard_id
TEXT
PRIMARY KEY, FK
Reference to the entries table.
integrity_score
REAL
CHECK (0.0 - 1.0)
Authenticity probability (Ghost Job Score).
alignment_score
REAL
CHECK (0.0 - 1.0)
Semantic match percentage (Candidate Alignment).
analysis_payload
TEXT
JSON
Metadata explaining module logic or reasoning.
updated_at
DATETIME
DEFAULT CURRENT_TIMESTAMP
Timestamp of last analysis.



3.0 Initial Database Schema (DDL)
-- Enable WAL mode for concurrency
PRAGMA journal_mode = WAL;

-- Create entries table
CREATE TABLE IF NOT EXISTS entries (
    vanguard_id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL,
    identity_manifest TEXT NOT NULL,
    entry_data TEXT NOT NULL,
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    hit_count INTEGER DEFAULT 1,
    status TEXT DEFAULT 'active'
);

-- Create enrichment table
CREATE TABLE IF NOT EXISTS enrichment (
    vanguard_id TEXT PRIMARY KEY,
    integrity_score REAL CHECK (integrity_score >= 0.0 AND integrity_score <= 1.0),
    alignment_score REAL CHECK (alignment_score >= 0.0 AND alignment_score <= 1.0),
    analysis_payload TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vanguard_id) REFERENCES entries (vanguard_id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_entries_provider ON entries(provider_id);
CREATE INDEX IF NOT EXISTS idx_entries_last_seen ON entries(last_seen);
CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status);



4.0 Ingestion Logic (Upsert)
The ScoutCore maintains state using the following logic. This preserves the first_seen date while updating the last_seen heartbeat and resetting status to active if the entry re-appears in the environment.
INSERT INTO entries (vanguard_id, provider_id, identity_manifest, entry_data)
VALUES (?, ?, ?, ?)
ON CONFLICT(vanguard_id) DO UPDATE SET
    last_seen = CURRENT_TIMESTAMP,
    status = 'active';



5.0 Maintenance
To maintain system health and avoid state bloat, the ScoutCore executes a daily purge of entries where last_seen exceeds the domain-specific TTL (Time To Live).
$$TTL\_Removal = \text{last\_seen} < (CURRENT\_TIMESTAMP - \text{Domain\_Threshold})$$


