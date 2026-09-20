PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS seats (
    seat_id TEXT PRIMARY KEY,
    cursor_event_id TEXT NOT NULL,
    working_state_json TEXT NOT NULL,
    state_version INTEGER NOT NULL CHECK (state_version >= 0),
    status TEXT NOT NULL,
    occupancy_state TEXT NOT NULL CHECK (occupancy_state IN ('AVAILABLE','OCCUPIED')),
    current_wake_id TEXT UNIQUE,
    policy_ref TEXT NOT NULL,
    operator_profile_ref TEXT NOT NULL,
    authority_profile_ref TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    seat_id TEXT,
    event_kind TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wakes (
    wake_id TEXT PRIMARY KEY,
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    basis_version INTEGER NOT NULL,
    basis_cursor_event_id TEXT NOT NULL,
    status TEXT NOT NULL,
    outcome TEXT,
    created_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS operators (
    operator_id TEXT PRIMARY KEY,
    registered INTEGER NOT NULL CHECK (registered IN (0,1)),
    available INTEGER NOT NULL CHECK (available IN (0,1)),
    authority_required INTEGER NOT NULL CHECK (authority_required IN (0,1)),
    adapter_kind TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS seat_operator_eligibility (
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    operator_id TEXT NOT NULL REFERENCES operators(operator_id),
    eligible INTEGER NOT NULL CHECK (eligible IN (0,1)),
    PRIMARY KEY (seat_id, operator_id)
);

CREATE TABLE IF NOT EXISTS seat_operator_authority (
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    operator_id TEXT NOT NULL REFERENCES operators(operator_id),
    authorized INTEGER NOT NULL CHECK (authorized IN (0,1)),
    authority_ref TEXT,
    PRIMARY KEY (seat_id, operator_id)
);

CREATE TABLE IF NOT EXISTS declared_tests (
    test_id TEXT PRIMARY KEY,
    argv_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS operator_invocations (
    operator_invocation_id TEXT PRIMARY KEY,
    wake_id TEXT NOT NULL REFERENCES wakes(wake_id),
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    operator_id TEXT NOT NULL REFERENCES operators(operator_id),
    status TEXT NOT NULL,
    args_json TEXT NOT NULL,
    result_json TEXT
);

CREATE TABLE IF NOT EXISTS action_requests (
    request_id TEXT PRIMARY KEY,
    wake_id TEXT NOT NULL REFERENCES wakes(wake_id),
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    operator_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    authority_ref TEXT
);

CREATE TABLE IF NOT EXISTS semantic_requests (
    request_id TEXT PRIMARY KEY,
    wake_id TEXT NOT NULL REFERENCES wakes(wake_id),
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    basis_version INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS semantic_proposals (
    proposal_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL REFERENCES semantic_requests(request_id),
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS outputs (
    output_id TEXT PRIMARY KEY,
    wake_id TEXT NOT NULL REFERENCES wakes(wake_id),
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    output_kind TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transitions (
    transition_id TEXT PRIMARY KEY,
    wake_id TEXT NOT NULL UNIQUE REFERENCES wakes(wake_id),
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    prior_version INTEGER NOT NULL,
    resulting_version INTEGER NOT NULL,
    prior_cursor_event_id TEXT NOT NULL,
    resulting_cursor_event_id TEXT NOT NULL,
    prior_working_state_json TEXT NOT NULL,
    resulting_working_state_json TEXT NOT NULL,
    consumed_events_json TEXT NOT NULL,
    accepted_outputs_json TEXT NOT NULL,
    accepted_operator_invocations_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS receipts (
    receipt_id TEXT PRIMARY KEY,
    receipt_kind TEXT NOT NULL,
    wake_id TEXT NOT NULL REFERENCES wakes(wake_id),
    seat_id TEXT NOT NULL REFERENCES seats(seat_id),
    subject_id TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_seat_seq ON events(seat_id, seq);
CREATE INDEX IF NOT EXISTS idx_wakes_seat ON wakes(seat_id);
CREATE INDEX IF NOT EXISTS idx_invocations_wake ON operator_invocations(wake_id);
CREATE INDEX IF NOT EXISTS idx_outputs_wake ON outputs(wake_id);
