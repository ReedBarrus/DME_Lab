PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS wake_opportunities (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id TEXT NOT NULL UNIQUE,
    opportunity_sha256 TEXT NOT NULL,
    seat_id TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    request_id TEXT,
    request_sha256 TEXT,
    selection_ref TEXT,
    selection_sha256 TEXT,
    preparation_kind TEXT,
    opportunity_basis TEXT NOT NULL,
    max_consumed_events INTEGER NOT NULL CHECK (max_consumed_events >= 0 AND max_consumed_events <= 32),
    opportunity_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reentry_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    opportunity_id TEXT NOT NULL REFERENCES wake_opportunities(opportunity_id),
    wake_id TEXT NOT NULL,
    seat_id TEXT NOT NULL,
    event_kind TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reentry_receipts (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id TEXT NOT NULL UNIQUE,
    receipt_sha256 TEXT NOT NULL,
    opportunity_id TEXT NOT NULL UNIQUE REFERENCES wake_opportunities(opportunity_id),
    wake_id TEXT NOT NULL,
    seat_id TEXT NOT NULL,
    outcome TEXT NOT NULL,
    preparation_receipt_id TEXT,
    controller_receipt_id TEXT,
    receipt_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reentry_events_opportunity
ON reentry_events(opportunity_id, seq);

CREATE INDEX IF NOT EXISTS idx_reentry_receipts_seat
ON reentry_receipts(seat_id, seq);
