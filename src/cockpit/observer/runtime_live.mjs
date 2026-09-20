function text(tag, value, className = '') {
  const node = document.createElement(tag);
  node.textContent = value == null ? '—' : String(value);
  if (className) node.className = className;
  return node;
}

function metric(label, value) {
  const item = document.createElement('div');
  item.className = 'runtime-metric';
  item.append(text('span', label, 'runtime-metric-label'));
  item.append(text('strong', value, 'runtime-metric-value'));
  return item;
}

function row(values) {
  const item = document.createElement('div');
  item.className = 'runtime-row';
  values.forEach((value) => item.append(text('span', value)));
  return item;
}

function renderUnavailable(root, message) {
  root.replaceChildren();
  root.className = 'runtime-panel runtime-unavailable';
  root.append(text('h2', 'LIVE RUNTIME'));
  root.append(text('p', message));
  root.append(text('p', 'Projection only. Durable stores remain authoritative.', 'runtime-footnote'));
}

function renderSnapshot(root, snapshot) {
  const state = snapshot?.state;
  if (!state) {
    renderUnavailable(root, 'Runtime snapshot missing state.');
    return;
  }

  root.replaceChildren();
  root.className = 'runtime-panel';
  root.dataset.stateSha256 = snapshot.state_sha256 || '';

  const header = document.createElement('div');
  header.className = 'runtime-header';
  header.append(text('h2', 'LIVE TERRARIUM'));
  header.append(
    text(
      'p',
      `${state.projection_status || 'UNKNOWN'} · state ${(snapshot.state_sha256 || '').slice(0, 12)}`,
      'runtime-subtitle',
    ),
  );
  root.append(header);

  const occupied = state.active_operations?.occupied_seats?.length || 0;
  const metrics = document.createElement('div');
  metrics.className = 'runtime-metrics';
  metrics.append(
    metric('SEATS', state.seats?.length || 0),
    metric('OCCUPIED', occupied),
    metric('CAMPAIGNS', state.campaigns?.length || 0),
    metric('REQUESTS', state.requests?.length || 0),
    metric('SELECTED', state.current_selection?.length || 0),
    metric('PREP', state.preparation_receipts?.length || 0),
    metric('ACTIVE LEASES', state.active_model_leases?.length || 0),
    metric('ACTION REQUESTS', state.authority?.action_requests?.length || 0),
  );
  root.append(metrics);

  const grid = document.createElement('div');
  grid.className = 'runtime-grid';

  const seats = document.createElement('section');
  seats.className = 'runtime-block';
  seats.append(text('h3', 'SEATS'));
  if (!state.seats?.length) {
    seats.append(text('p', 'No projected seats.'));
  } else {
    state.seats.forEach((seat) => {
      seats.append(
        row([
          seat.seat_id,
          seat.occupancy_state,
          seat.current_wake_id || '—',
          `v${seat.state_version}`,
        ]),
      );
    });
  }
  grid.append(seats);

  const attention = document.createElement('section');
  attention.className = 'runtime-block';
  attention.append(text('h3', 'SELECTED / PREPARATION'));
  if (!state.preparation_readiness?.length) {
    attention.append(text('p', 'No currently selected preparation projection.'));
  } else {
    state.preparation_readiness.forEach((item) => {
      attention.append(
        row([
          item.request_id,
          item.relation_id,
          item.request_applicability,
          item.readiness,
        ]),
      );
    });
  }
  grid.append(attention);

  const gear = document.createElement('section');
  gear.className = 'runtime-block';
  gear.append(text('h3', 'GEAR'));
  if (!state.model_resources?.length) {
    gear.append(text('p', 'No projected model resources.'));
  } else {
    const activeByResource = new Map(
      (state.active_model_leases || []).map((lease) => [lease.resource_id, lease]),
    );
    state.model_resources.forEach((resource) => {
      const lease = activeByResource.get(resource.resource_id);
      gear.append(
        row([
          resource.resource_id,
          resource.provider,
          resource.status,
          lease ? `LEASED → ${lease.seat_id}` : 'UNLEASED',
        ]),
      );
    });
  }
  grid.append(gear);

  const consequence = document.createElement('section');
  consequence.className = 'runtime-block';
  consequence.append(text('h3', 'ACTIVE CONSEQUENCE / AUTHORITY'));
  consequence.append(
    row([
      'active wakes',
      state.active_operations?.active_wakes?.length || 0,
      'active invocations',
      state.active_operations?.active_operator_invocations?.length || 0,
    ]),
  );
  consequence.append(
    row([
      'action requests',
      state.authority?.action_requests?.length || 0,
      'projection authority',
      state.authority_effect,
    ]),
  );
  grid.append(consequence);

  root.append(grid);

  const diagnostics = document.createElement('div');
  diagnostics.className = 'runtime-diagnostics';
  diagnostics.append(
    text(
      'p',
      `cross-store atomicity: ${state.cross_store_atomicity}`,
      'runtime-footnote',
    ),
  );
  const unavailable = (state.sources || []).filter(
    (source) => source.status !== 'AVAILABLE' && source.status !== 'NOT_CONFIGURED',
  );
  if (unavailable.length) {
    diagnostics.append(
      text(
        'p',
        `partial sources: ${unavailable.map((source) => source.source).join(', ')}`,
        'runtime-warning',
      ),
    );
  }
  if (state.standing_movement_history?.status) {
    diagnostics.append(
      text(
        'p',
        `standing history: ${state.standing_movement_history.status}`,
        'runtime-footnote',
      ),
    );
  }
  diagnostics.append(
    text(
      'p',
      'LIVE PROJECTION ≠ SOURCE OF TRUTH · DISPLAYED STATE ≠ AUTHORITY',
      'runtime-footnote',
    ),
  );
  root.append(diagnostics);
}

export function startRuntimeProjection(root) {
  if (!root) return null;

  const params = new URL(window.location.href).searchParams;
  const endpoint = params.get('runtime');
  if (!endpoint) {
    renderUnavailable(
      root,
      'Runtime sidecar not configured. Add ?runtime=http://127.0.0.1:8765/runtime/events to subscribe.',
    );
    return null;
  }

  renderUnavailable(root, 'Connecting to durable runtime projection…');
  const source = new EventSource(endpoint);

  source.addEventListener('runtime_projection', (event) => {
    try {
      renderSnapshot(root, JSON.parse(event.data));
      root.dataset.runtimeState = 'live';
    } catch (error) {
      renderUnavailable(root, `Runtime projection parse failure: ${error}`);
      root.dataset.runtimeState = 'invalid';
    }
  });

  source.onerror = () => {
    if (root.dataset.runtimeState !== 'live') {
      renderUnavailable(
        root,
        'Live runtime sidecar unavailable. Static repository Cockpit remains valid independently.',
      );
    } else {
      root.dataset.runtimeState = 'reconnecting';
    }
  };

  return source;
}
