# DME Cockpit Desktop Launcher v0

## Status

**Candidate implementation — not yet promoted as a standing product surface.**

This package exists to pressure one operational question:

> Can the read-only Cockpit become a one-click local instrument without gaining
> repository mutation authority or silently displaying stale derived state as if
> it were current?

The launcher is convenience infrastructure around the existing bounded Cockpit
projection. It does not change the Cockpit's evidentiary authority.

---

## Pressure target

The current browser workflow requires a human to:

1. generate `generated/cockpit_projection.json`;
2. start a local HTTP server;
3. open the observer route;
4. remember which committed source basis was projected;
5. keep stale generated output from surviving a failed regeneration.

That friction is acceptable for development but weak for an instrument intended
to become routinely operational.

The desktop-launcher pressure is therefore:

    one click
    ->
    establish repo
    ->
    generate from exact committed ref
    ->
    serve only on loopback
    ->
    open read-only observer
    ->
    stop server when app closes

without:

    write authority to repository source
    branch/ref mutation
    silent stale fallback
    network freshness claims that were not observed

---

## v0 behavior

The launcher lives at:

`src/cockpit/desktop_launcher.py`

By default on Windows it:

- locates DME_Lab from `--repo`, `DME_LAB_REPO`, saved config, nearby
  repository ancestry, or a first-run folder picker;
- projects from `HEAD`;
- compares freshness against locally available `origin/main`, otherwise
  `main`, otherwise leaves freshness unknown;
- performs **no network fetch** to manufacture freshness;
- generates the projection before starting a server;
- relies on the existing generator's fail-closed behavior, which removes stale
  projection output on generation failure;
- binds an HTTP server only to `127.0.0.1`;
- launches Microsoft Edge in app mode with a dedicated local profile;
- shuts the server down when that app process exits.

On non-Windows systems, browser mode is available as a development fallback.

The launcher writes only:

- ignored derived projection output under `generated/`;
- user-local launcher configuration under the operating-system config
  directory;
- a user-local Edge profile for the app-mode window.

It does not write source artifacts, Git refs, commits, branches, or repository
standing.

---

## VS Code workflow

The repository task:

`DME: Launch Cockpit`

runs the launcher from the workspace root.

This is the development path for exercising the exact same launch logic before
packaging it.

---

## Windows executable workflow

`tools/build_cockpit_windows.ps1`

packages the launcher with PyInstaller into:

`dist/cockpit/DME Cockpit.exe`

PyInstaller is intentionally **not** installed automatically. The build script
fails with an explicit instruction if the dependency is absent.

After one launch with the repository resolved, the executable can be pinned to
the Windows taskbar and reopened without VS Code.

No claim is made yet that the packaged executable has been built or tested on a
real Windows host.

---

## Failure semantics

The launcher should fail closed.

### Projection generation failure

Expected consequence:

    no HTTP server
    no browser/app window
    stale generated projection removed by generator
    explicit failure surfaced

### Repository not found

Expected consequence:

    no projection attempt
    explicit folder selection or error

### Freshness comparison unavailable

Expected consequence:

    projection may still render
    freshness remains unknown
    no network operation is silently performed

### Edge unavailable on Windows

Expected consequence:

    edge-app launch fails explicitly

A caller may intentionally select browser mode instead. The launcher does not
silently broaden its execution surface.

---

## Tests

`tests/cockpit/test_desktop_launcher.py` pressures:

- explicit repository validation and remembered configuration;
- rejection of non-repository paths;
- local freshness-ref selection;
- loopback-only serving;
- projection failure before server creation;
- Edge app-mode command construction with a dedicated profile.

These tests are implementation evidence only. They do not establish the
packaged Windows executable works on the user's machine.

---

## Claim ceiling

If v0 survives local Windows use, the strongest warranted statement is:

> The existing read-only Cockpit can be launched as a one-click local desktop
> instrument while preserving the tested source/projection boundary and without
> granting the launcher repository write authority.

It would **not** establish:

- production readiness;
- installer quality;
- cross-platform desktop support;
- security hardening against hostile local users;
- automatic repository synchronization;
- network freshness;
- authoritative world state;
- that the Cockpit itself is a finished product.

---

## Next pressure after local use

The useful next evidence is not more polish.

It is:

    repeated ordinary launch
    restart after repo movement
    projection-generation failure
    stale local origin/main
    Edge process exit
    branch checkout change
    taskbar launch outside VS Code

and whether each case remains legible without widening authority or displaying
an older projection as current.
