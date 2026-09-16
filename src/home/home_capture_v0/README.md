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

## Ordinary Windows use

Double-click:

```text
Home Capture.vbs
```

The launcher:

1. checks whether the correct Home service is already healthy;
2. starts the Python server invisibly only when needed;
3. waits for operational health;
4. opens Home in an Edge/Chrome app window when available, otherwise in the
   default browser;
5. displays a graphical error if startup fails.

No terminal is required. A Desktop or Start-menu shortcut may point directly
to `Home Capture.vbs`. The VBS + PowerShell pair is the smallest Windows-native
launcher for this experimental source checkout; no binary build is required.

`start_home.bat` remains a compatibility entry point and calls the same
launcher.

Opening `index.html` directly is intentionally inert. It explains that Home is
not running and disables SAVE, history, and export instead of suggesting that
persistence is available.

## Durable data

Runtime state is contained under:

```text
data/home_capture.sqlite3
data/exports/
data/logs/
```

`data/` is ignored by Git. If the older `home_capture.sqlite3` exists beside
the source and the new database does not, the server moves it into `data/` on
first startup. If both exist, the explicit `data/` database wins and the legacy
file is left untouched.

The UI displays the retained count and provides lane filters, raw-text search,
chronological ordering, entry selection, stable refs, timestamps, and JSONL
download. It does not edit, delete, interpret, relate, or rewrite captures.

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

Run focused tests from the repository root:

```powershell
python -m unittest tests.home.test_home_capture
```

## Explicit boundary

Home Capture v0 gathers user-authored evidence only. It does not add Explore,
inferred needs, inferred commitments, relation extraction, automatic collision
detection, psychological classification, DME standing, autonomous agent access,
or audio retention.
