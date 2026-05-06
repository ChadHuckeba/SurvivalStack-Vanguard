-- Enable WAL mode for concurrency
PRAGMA journal_mode = WAL;

-- Create entries table
CREATE TABLE IF NOT EXISTS entries (
    vanguard_id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL,
    identity_manifest TEXT NOT NULL, -- JSON array of keys used for ID generation
    entry_data TEXT NOT NULL,        -- JSON blob of the raw lead content
    work_model TEXT DEFAULT 'unknown',
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    hit_count INTEGER DEFAULT 1,
    status TEXT DEFAULT 'active',
    career_url TEXT,
    career_discovery_method TEXT,
    career_extraction_status TEXT DEFAULT 'pending',
    career_error_log TEXT
);

-- Enrichment Table
CREATE TABLE IF NOT EXISTS enrichment (
    vanguard_id TEXT PRIMARY KEY,
    integrity_score REAL CHECK (integrity_score >= 0.0 AND integrity_score <= 1.0),
    alignment_score REAL CHECK (alignment_score >= 0.0 AND alignment_score <= 1.0),
    analysis_payload TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vanguard_id) REFERENCES entries (vanguard_id) ON DELETE CASCADE
);

-- Company Registry Table
CREATE TABLE IF NOT EXISTS companies (
    company_name TEXT PRIMARY KEY,
    root_domain TEXT,
    career_url TEXT,
    ats_provider TEXT,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_entries_provider ON entries(provider_id);
CREATE INDEX IF NOT EXISTS idx_entries_last_seen ON entries(last_seen);
CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status);
CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(root_domain);
