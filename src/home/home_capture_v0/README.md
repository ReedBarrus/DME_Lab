# Home Capture v0

A deliberately small capture device for gathering raw user-authored evidence.
It does not interpret captures or create DME standing.

## Visible lanes

- **CARE** — raw care, need, or capacity evidence. It creates no commitment.
- **COMMIT** — deliberate user-authored adoption. Saving in this lane is the
  only current capture operation that records an explicit personal commitment.
- **DEVELOP** — deliberate DME, build, or experimental-work evidence. It does
  not create DME standing or automatically create a personal commitment.
- **EXPLORE is intentionally absent.**

Each capture retains a stable ref, lane, unmodified raw text, explicit origin,
client timestamp when supplied, and server UTC timestamp.

COMMIT additionally creates a stable active commitment. Optional `start_at`,
`end_at`, and `report_at` values are temporal projections, not predictions.
An active commitment whose report time has arrived is shown as `REPORT_DUE`
but remains active until the user explicitly records `COMPLETED`, `REVISED`,
`RELEASED`, `BYPASSED`, or `FORGOTTEN`. `REVISED` creates a new COMMIT capture
and retains only the original commitment's `revised_by` replacement reference.

## Recurring commitments

Recurrence is a property of the same commitment primitive, not a second task,
habit, ritual, reminder, or event ontology. A commitment is either `NONE`
(one-shot) or `WEEKLY_PATTERN`. Weekly patterns select one or more of `MON`
through `SUN` and may carry one optional coarse placement: `ANYTIME`,
`MORNING`, `AFTERNOON`, or `EVENING`.

A recurring commitment keeps one stable commitment ID across every expected
local day. An occurrence report records that ID, its intended local date, the
report timestamp, optional `MET`, `PARTIAL`, `NOT_MET`, or `NOT_APPLICABLE`,
and optional exact raw feedback. Reporting an occurrence never closes the
parent. Only the existing explicit commitment-resolution operation can do so.
Missing reports project as `NO_REPORT`; Home does not translate missingness or
`NOT_MET` into bypass, forgetting, release, completion, cause, or failure.

The commitment identity is separate from its append-only specification
history. Every commitment begins with one `INITIAL` specification. An active
commitment may add a `RECORDING_CORRECTION` or `INTENTION_CHANGE` specification
without changing its commitment ID or closing it. The current projection uses
the current specification while every prior statement, recurrence coordinate,
amendment kind, optional exact reason, and lineage reference remains
inspectable. Terminal `REVISED` remains a different operation: it closes the
original identity and creates a replacement commitment.

Occurrence reports retain the applicable specification ID. A later amendment
therefore cannot silently change which specification a retained report was
made under. The old commitment columns remain migration-era compatibility
snapshots only; versioned specifications are the current configuration source.

The UI separates active one-shot commitments, the seven-day Regular Week,
today's low-interaction report pass, and chronological recurrence history.
The week is a navigational load projection only: there are no streaks, scores,
percentages, compliance metrics, trend claims, or automatic rebalancing.

## Ordinary Windows use

Double-click:

```text
Home Capture.exe
```

The native Windows launcher:

1. checks whether the correct Home service is already healthy;
2. starts the Python server invisibly only when needed;
3. waits for operational health;
4. opens Home in an Edge/Chrome app window when available, otherwise in the
   default browser;
5. displays a graphical error if startup fails.

No terminal, PowerShell interaction, or administrator permission is required
for ordinary use. A Desktop or Start-menu shortcut may point directly to
`Home Capture.exe`; the launcher resolves `server.py` and `data/` relative to
the executable rather than the shortcut's working directory.

The VBS, PowerShell, and batch launchers remain available for development and
debugging.

Opening `index.html` directly is intentionally inert. It explains that Home is
not running and disables SAVE, history, and export instead of suggesting that
persistence is available.

## Durable data

Runtime state is contained under:

```text
data/home_capture.sqlite3
data/backups/
data/exports/
data/logs/
```

`data/` is ignored by Git. If the older `home_capture.sqlite3` exists beside
the source and the new database does not, the server moves it into `data/` on
first startup. If both exist, the explicit `data/` database wins and the legacy
file is left untouched.

On the first lifecycle-schema migration, Home creates a consistent SQLite
backup under `data/backups/` before changing the database. The migration is
idempotent: every existing COMMIT capture is associated with one deterministic
active commitment, with all schedule fields left null. It never rewrites the
original capture row.

The UI separates CARE history, active commitments, report-due commitments,
closed commitment history, and DEVELOP history. Explicit resolution changes
commitment standing but does not edit, delete, interpret, or rewrite captures.
JSONL export remains the immutable raw-capture surface.

Scheduled commitments can be downloaded as `.ics` calendar events. A user-set
first time can also generate a recurring daily `HOME COMMITMENT REPORT` event.
Calendar files are one-way reminder projections: importing, changing, or
deleting them never changes Home. Direct calendar synchronization, delivery
confirmation, credentials, and phone-notification guarantees are not provided.

## Future notes and Chat Home

Home also retains explicit scheduled continuation events independently from
commitments. Events move only through `SCHEDULED`, `DUE`, `ACKNOWLEDGED`, or
`CANCELLED`. The backend process detects due times even when no browser window
is open and makes a best-effort local Windows notification when an event first
becomes due. `DUE` means returned to attention, not executed; acknowledgement
means the event was seen, not that its requested consequence succeeded.

Chat Home is a separately attributed continuation surface for current pressure,
recommendations, unresolved questions, continuation references, future notes,
and executable agent commitments. It is not Reed Home. Recommendations and
future notes are not commitments. The API accepts an agent commitment only when
the record includes a non-empty explicit execution path.

The authoritative event and Chat records remain in SQLite. Home regenerates
the following bounded, non-authoritative projections atomically:

```text
data/agent_bridge/chat_now.json
data/agent_bridge/due_events.json
```

They are also readable locally at `/agent_bridge/chat_now.json` and
`/agent_bridge/due_events.json`. They contain Chat continuation state and due
Chat-targeted events only; unrelated capture history is excluded. Nothing in
this version transports or executes a due instruction, exposes Home publicly,
or connects to ChatGPT task scheduling.

## Trusted-LAN phone access

Double-click:

```text
Home Capture LAN.vbs
```

This explicitly binds the same authoritative PC-hosted database to the trusted
LAN and displays the phone URL in the UI. A phone on the same network may use
that URL; captures appear in the desktop history during its five-second refresh.

Do not forward port `8765`, expose it to the public internet, or use LAN mode on
an untrusted network. No authentication, synchronization, second database, or
public-internet service is implemented. Windows Firewall may prompt on first LAN
use; allow Python only on **Private networks** if phone access is wanted.

If Home is already running in desktop-only mode, the LAN launcher refuses to
start a duplicate. Close the existing Python process before deliberately
switching to LAN mode.

## Development and validation

Direct server use remains available for bounded testing:

```powershell
python server.py --host 127.0.0.1 --port 8765 --access-mode desktop
python server.py --host 0.0.0.0 --port 8765 --access-mode lan
```

No third-party Python packages are required.

Rebuild the native launcher with the Windows-provided .NET Framework compiler:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\build_home_capture.ps1
```

The script reproducibly generates the application icon and emits
`Home Capture.exe` beside `server.py`. It writes build intermediates only under
`build/`; it never reads, replaces, or removes `data/`.

The executable is locally built and unsigned. Windows may display an unknown
publisher or SmartScreen warning, particularly after the file is copied or
downloaded. Code signing is not part of this experimental package.

Run focused tests from the repository root:

```powershell
python -m unittest tests.home.test_home_capture
```

## Explicit boundary

Home Capture v0 retains explicit user-authored and actor-attributed state. It does not add Explore,
inferred needs, inferred commitments, relation extraction, automatic collision
detection, psychological classification, DME standing, autonomous agent access,
instruction execution, public transport, recurring-calendar synchronization,
arbitrary recurrence grammar, adherence inference, or audio retention.
