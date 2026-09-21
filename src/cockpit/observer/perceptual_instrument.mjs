export const PROJECTION_NAMES = Object.freeze(['CONSEQUENCE', 'TOPOLOGY']);
export const SCALE_NAMES = Object.freeze(['WORLD', 'CAMPAIGN', 'SEAT_PROCESS', 'OBJECT']);

const array = (value) => Array.isArray(value) ? value : [];
const objects = (rows, field) => array(rows)
  .map((row) => row && row[field])
  .filter((value) => value && typeof value === 'object');

export const addressKey = (item) =>
  item && item.kind && item.id != null
    ? String(item.kind) + ':' + String(item.id)
    : '';

const address = (kind, id) => ({kind: String(kind), id: String(id)});

function outstandingAssignments(state) {
  const live = new Map();
  for (const event of objects(state.assignment_history, 'event_json')) {
    if (!event.assignment_id) continue;
    if (event.assignment_kind === 'ASSIGNED') live.set(event.assignment_id, event);
    if (event.assignment_kind === 'ASSIGNMENT_RELEASED') live.delete(event.assignment_id);
  }
  for (const satisfaction of objects(state.assignment_satisfactions, 'satisfaction_json')) {
    if (satisfaction.assignment_id) live.delete(satisfaction.assignment_id);
  }
  return [...live.values()];
}

export function buildOperationalGraph(snapshot) {
  const state = snapshot?.state || {};
  const nodes = [];
  const edges = [];
  const byKey = new Map();

  const addNode = (kind, id, label, raw, meta = {}) => {
    if (!id) return;
    const itemAddress = address(kind, id);
    const key = addressKey(itemAddress);
    if (byKey.has(key)) return;
    const node = {
      key,
      address: itemAddress,
      kind,
      id: String(id),
      label: label || String(id),
      raw,
      meta,
    };
    nodes.push(node);
    byKey.set(key, node);
  };

  const addEdge = (source, target, relation) => {
    const sourceKey = addressKey(source);
    const targetKey = addressKey(target);
    if (!byKey.has(sourceKey) || !byKey.has(targetKey)) return;
    if (
      edges.some(
        (edge) =>
          edge.sourceKey === sourceKey
          && edge.targetKey === targetKey
          && edge.relation === relation,
      )
    ) return;
    edges.push({source, target, sourceKey, targetKey, relation});
  };

  const horizons = new Map(
    array(state.development_horizons?.horizons).map(
      (item) => [item.campaign_id, item],
    ),
  );

  for (const row of array(state.campaigns)) {
    const campaign = row?.campaign_json;
    if (!campaign?.campaign_id) continue;
    addNode(
      'campaign',
      campaign.campaign_id,
      campaign.title || campaign.campaign_id,
      campaign,
      {
        horizon_state:
          horizons.get(campaign.campaign_id)?.horizon_state || 'UNPROJECTED',
        campaign_sha256: row.campaign_sha256 || null,
      },
    );
  }

  const selected = new Set(
    array(state.current_selection)
      .map((item) => item?.request_id)
      .filter(Boolean),
  );

  for (const request of objects(state.requests, 'request_json')) {
    if (!request.request_id) continue;
    addNode(
      'request',
      request.request_id,
      request.title || request.relation_id || request.request_id,
      request,
      {
        selected: selected.has(request.request_id),
        campaign_id: request.campaign_id || null,
      },
    );
  }

  for (const seat of array(state.seats)) {
    if (!seat?.seat_id) continue;
    addNode('seat', seat.seat_id, seat.seat_id, seat, {
      occupancy_state: seat.occupancy_state || 'UNKNOWN',
      current_wake_id: seat.current_wake_id || null,
    });
  }

  for (const assignment of outstandingAssignments(state)) {
    addNode(
      'assignment',
      assignment.assignment_id,
      assignment.assignment_id,
      assignment,
      {
        assignment_state: 'OUTSTANDING',
        campaign_id: assignment.campaign_id || null,
      },
    );
  }

  for (const bell of objects(state.manual_bells, 'bell_json')) {
    const id = bell.bell_id || bell.manual_bell_id;
    if (id) addNode('bell', id, id, bell);
  }

  for (const wake of objects(state.reentry_opportunities, 'opportunity_json')) {
    if (wake.opportunity_id) {
      addNode('wake', wake.opportunity_id, wake.opportunity_id, wake);
    }
  }

  for (const [kind, source] of [
    ['preparation_receipt', state.preparation_receipts],
    ['reentry_receipt', state.reentry_receipts],
    ['execution_receipt', state.execution_receipts],
  ]) {
    for (const receipt of objects(source, 'receipt_json')) {
      const id =
        receipt.receipt_id
        || receipt.preparation_id
        || receipt.execution_receipt_id;
      if (id) addNode(kind, id, id, receipt);
    }
  }

  for (const lease of array(state.active_model_leases)) {
    if (lease?.lease_id) {
      addNode(
        'model_lease',
        lease.lease_id,
        lease.resource_id || lease.lease_id,
        lease,
        {seat_id: lease.seat_id || null, status: lease.status || null},
      );
    }
  }

  for (const invocation of array(
    state.active_operations?.active_operator_invocations,
  )) {
    const id = invocation?.invocation_id || invocation?.operator_invocation_id;
    if (id) addNode('process', id, invocation.operator_id || id, invocation);
  }

  for (const incident of array(state.incidents)) {
    const raw = incident?.incident_json || incident;
    const id = raw?.incident_id;
    if (id) addNode('incident', id, raw.title || id, raw);
  }

  for (const node of nodes) {
    const raw = node.raw || {};

    if (node.kind === 'request' && raw.campaign_id) {
      addEdge(
        address('campaign', raw.campaign_id),
        node.address,
        'declares_request',
      );
    }

    if (node.kind === 'assignment') {
      if (raw.request_id) {
        addEdge(
          address('request', raw.request_id),
          node.address,
          'assigned_as',
        );
      }
      if (raw.seat_id) {
        addEdge(
          address('seat', raw.seat_id),
          node.address,
          'assigned_to',
        );
      }
    }

    if (node.kind === 'bell' && raw.assignment_id) {
      addEdge(
        address('assignment', raw.assignment_id),
        node.address,
        'rings',
      );
    }

    if (node.kind === 'wake') {
      if (raw.assignment_id) {
        addEdge(
          address('assignment', raw.assignment_id),
          node.address,
          'permits_wake_opportunity',
        );
      }
      if (raw.seat_id) {
        addEdge(
          address('seat', raw.seat_id),
          node.address,
          'wake_for',
        );
      }
      if (raw.bell_id || raw.source_bell_id) {
        addEdge(
          address('bell', raw.bell_id || raw.source_bell_id),
          node.address,
          'emits',
        );
      }
    }

    if (node.kind.endsWith('receipt')) {
      if (raw.request_id) {
        addEdge(
          address('request', raw.request_id),
          node.address,
          'has_receipt',
        );
      }
      if (raw.opportunity_id) {
        addEdge(
          address('wake', raw.opportunity_id),
          node.address,
          'has_receipt',
        );
      }
    }

    if (node.kind === 'model_lease' && raw.seat_id) {
      addEdge(
        address('seat', raw.seat_id),
        node.address,
        'leases_model',
      );
    }

    if (node.kind === 'process') {
      if (raw.seat_id) {
        addEdge(address('seat', raw.seat_id), node.address, 'runs_process');
      }
      if (raw.wake_id) {
        const matchingWake = nodes.find(
          (candidate) =>
            candidate.kind === 'wake'
            && candidate.raw?.wake_id === raw.wake_id,
        );
        if (matchingWake) {
          addEdge(matchingWake.address, node.address, 'invokes');
        }
      }
    }
  }

  return {
    nodes,
    edges,
    byKey,
    snapshot_sha256: snapshot?.state_sha256 || null,
  };
}

export function toggleAddressSelection(current, next, additive = false) {
  const key = addressKey(next);
  const existing = array(current);
  if (!key) return existing;
  if (!additive) return [next];
  return existing.some((item) => addressKey(item) === key)
    ? existing.filter((item) => addressKey(item) !== key)
    : [...existing, next];
}

export function projectionAddressStatus(
  projection,
  addresses,
  graph,
  observerModel = null,
) {
  const selected = array(addresses);
  if (!selected.length) return {status: 'EMPTY', missing: []};

  const missing = selected.filter((item) => {
    const operationallyPresent = Boolean(
      graph?.byKey?.has(addressKey(item)),
    );
    if (projection !== 'TOPOLOGY') return !operationallyPresent;
    const semanticallyPresent = Boolean(
      observerAddressObject(observerModel, item),
    );
    return !operationallyPresent && !semanticallyPresent;
  });

  return {
    status: missing.length
      ? 'ADDRESS_NOT_REPRESENTABLE'
      : 'REPRESENTABLE',
    missing,
  };
}

export function observerAddressObject(observerModel, itemAddress) {
  if (!observerModel || !itemAddress) return null;

  if (itemAddress.kind === 'pressure_occurrence') {
    const occurrence = observerModel.occurrences?.find(
      (item) => item.key === itemAddress.id,
    );
    return occurrence
      ? {
          label: occurrence.node?.title || occurrence.node?.id || itemAddress.id,
          raw: occurrence.node,
          relationBasis: 'normalized pressure relation',
        }
      : null;
  }

  if (itemAddress.kind === 'constraint') {
    const occurrence = observerModel.constraintOccurrences?.find(
      (item) => item.key === itemAddress.id,
    );
    return occurrence
      ? {
          label: occurrence.constraint?.id || itemAddress.id,
          raw: occurrence.constraint,
          relationBasis: 'normalized constraint occurrence',
        }
      : null;
  }

  if (itemAddress.kind === 'evidence') {
    const occurrence = observerModel.evidenceOccurrences?.find(
      (item) => item.key === itemAddress.id,
    );
    return occurrence
      ? {
          label: occurrence.reference?.id || itemAddress.id,
          raw: occurrence.reference,
          relationBasis: 'normalized evidence occurrence',
        }
      : null;
  }

  if (itemAddress.kind === 'projection_document') {
    const occurrence = observerModel.projectionDocumentOccurrences?.find(
      (item) => item.key === itemAddress.id,
    );
    return occurrence
      ? {
          label:
            occurrence.document?.title
            || occurrence.document?.source_path
            || itemAddress.id,
          raw: occurrence.document,
          relationBasis: 'normalized projection document',
        }
      : null;
  }

  return null;
}

export function observerAddressRelations(observerModel, itemAddress) {
  if (!observerModel || itemAddress?.kind !== 'pressure_occurrence') return [];
  return array(observerModel.semanticEdges)
    .filter(
      (edge) =>
        edge.sourceCandidates?.some(
          (item) => item.key === itemAddress.id,
        )
        || edge.targetCandidates?.some(
          (item) => item.key === itemAddress.id,
        ),
    )
    .map((edge) => ({
      relation: edge.relation?.relation_kind || 'unknown_relation',
      source: edge.sourceCandidates?.[0]?.key || null,
      target: edge.targetCandidates?.[0]?.key || null,
      drawable: Boolean(edge.drawable),
      ambiguous: Boolean(edge.ambiguous),
    }));
}

export function buildAddressedChatPacket({
  addresses,
  snapshot,
  repositoryState,
}) {
  return {
    schema: 'cockpit_address_context_v0',
    addresses: array(addresses).map((item) => ({
      kind: item.kind,
      id: String(item.id),
    })),
    runtime_state_sha256: snapshot?.state_sha256 || null,
    repository_source_commit: repositoryState?.source_commit || null,
    repository_source_ref: repositoryState?.source_ref || null,
    authority_effect: 'NONE',
    semantic_claim_effect: 'NONE',
    transport_effect: 'NONE',
  };
}

export function deriveContextualAffordances({
  addresses,
  snapshot,
  controlConfigured = false,
}) {
  const graph = buildOperationalGraph(snapshot);
  const selectedNodes = array(addresses)
    .map((item) => graph.byKey.get(addressKey(item)))
    .filter(Boolean);
  const byKind = (kind) =>
    selectedNodes.filter((node) => node.kind === kind);

  const result = [];
  if (array(addresses).length) {
    result.push({verb: 'CHAT', effect: 'LOCAL_CONTEXT_ONLY'});
  }
  if (array(addresses).length > 1) {
    result.push({verb: 'COMPARE', effect: 'LOCAL_VIEW_ONLY'});
  }
  if (byKind('campaign').length === 1) {
    result.push({verb: 'PLAN', effect: 'LOCAL_DRAFT_ONLY'});
  }

  if (!controlConfigured) return result;

  const selectedRequests = new Set(
    array(snapshot?.state?.current_selection)
      .map((item) => item?.request_id)
      .filter(Boolean),
  );

  if (
    byKind('request').length === 1
    && !selectedRequests.has(byKind('request')[0].id)
  ) {
    result.push({verb: 'FOCUS', effect: 'CONTROL_PREFILL_ONLY', admissibility: 'UNVERIFIED_UNTIL_EXACT_PREVIEW'});
  }

  if (
    byKind('request').length === 1
    && byKind('seat').length === 1
    && selectedRequests.has(byKind('request')[0].id)
  ) {
    result.push({verb: 'ASSIGN', effect: 'CONTROL_PREFILL_ONLY', admissibility: 'UNVERIFIED_UNTIL_EXACT_PREVIEW'});
  }

  if (byKind('assignment').length === 1) {
    result.push(
      {verb: 'RELEASE', effect: 'CONTROL_PREFILL_ONLY', admissibility: 'UNVERIFIED_UNTIL_EXACT_PREVIEW'},
      {verb: 'RING', effect: 'CONTROL_PREFILL_ONLY', admissibility: 'UNVERIFIED_UNTIL_EXACT_PREVIEW'},
    );
  }

  return result;
}

export function buildCampaignPlanDraft({
  addresses,
  snapshot,
  note = '',
}) {
  const graph = buildOperationalGraph(snapshot);
  const campaign = array(addresses)
    .map((item) => graph.byKey.get(addressKey(item)))
    .find((node) => node?.kind === 'campaign');

  if (!campaign) return null;

  return {
    schema: 'cockpit_campaign_plan_draft_v0',
    campaign_id: campaign.id,
    source_runtime_state_sha256: snapshot?.state_sha256 || null,
    note,
    adoption_effect: 'NONE',
    selection_effect: 'NONE',
    assignment_effect: 'NONE',
    priority_effect: 'NONE',
    authority_effect: 'NONE',
    execution_effect: 'NONE',
  };
}

export function visibleGraphForScale(graph, scale, addresses) {
  if (!graph || scale === 'WORLD') return graph;

  const selectedKeys = new Set(array(addresses).map(addressKey));
  let seedKeys = new Set();

  if (scale === 'OBJECT') {
    seedKeys = selectedKeys;
  } else if (scale === 'CAMPAIGN') {
    const campaignIds = new Set();
    for (const item of array(addresses)) {
      const node = graph.byKey.get(addressKey(item));
      if (node?.kind === 'campaign') campaignIds.add(node.id);
      if (node?.raw?.campaign_id) campaignIds.add(node.raw.campaign_id);
    }
    for (const node of graph.nodes) {
      if (
        (node.kind === 'campaign' && campaignIds.has(node.id))
        || campaignIds.has(node.raw?.campaign_id)
      ) seedKeys.add(node.key);
    }
  } else if (scale === 'SEAT_PROCESS') {
    for (const node of graph.nodes) {
      if (
        node.kind === 'seat'
        || node.kind === 'process'
        || node.kind === 'model_lease'
      ) seedKeys.add(node.key);
    }
    for (const item of array(addresses)) {
      const node = graph.byKey.get(addressKey(item));
      if (node?.kind === 'seat' || node?.kind === 'process') {
        seedKeys.add(node.key);
      }
    }
  }

  if (!seedKeys.size) seedKeys = selectedKeys;
  if (!seedKeys.size) return {nodes: [], edges: [], byKey: graph.byKey};

  const visible = new Set(seedKeys);
  for (const edge of graph.edges) {
    if (seedKeys.has(edge.sourceKey) || seedKeys.has(edge.targetKey)) {
      visible.add(edge.sourceKey);
      visible.add(edge.targetKey);
    }
  }

  return {
    nodes: graph.nodes.filter((node) => visible.has(node.key)),
    edges: graph.edges.filter(
      (edge) =>
        visible.has(edge.sourceKey)
        && visible.has(edge.targetKey),
    ),
    byKey: graph.byKey,
  };
}

const element = (tag, text = '', className = '') => {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
};

const svgElement = (tag) =>
  document.createElementNS('http://www.w3.org/2000/svg', tag);

function laneIndex(kind) {
  if (kind === 'campaign') return 0;
  if (kind === 'seat' || kind === 'model_lease') return 1;
  if (
    kind === 'request'
    || kind === 'assignment'
    || kind === 'bell'
    || kind === 'wake'
    || kind === 'process'
  ) return 2;
  return 3;
}

function laneLabel(index) {
  return [
    'CAMPAIGNS',
    'SEATS / MODELS',
    'CONSEQUENCE FLOW',
    'RECEIPTS / INCIDENTS',
  ][index];
}

function stateFor(node) {
  if (node.kind === 'campaign') {
    return node.meta.horizon_state || 'UNPROJECTED';
  }
  if (node.kind === 'request') {
    return node.meta.selected ? 'SELECTED' : 'AVAILABLE';
  }
  if (node.kind === 'seat') {
    return node.meta.occupancy_state || 'UNKNOWN';
  }
  if (node.kind === 'assignment') return 'OUTSTANDING';
  if (node.kind === 'model_lease') return node.meta.status || 'LEASE';
  return node.kind.replaceAll('_', ' ').toUpperCase();
}

function controlPrefill(verb, addresses, snapshot) {
  const graph = buildOperationalGraph(snapshot);
  const nodes = addresses
    .map((item) => graph.byKey.get(addressKey(item)))
    .filter(Boolean);

  const request = nodes.find((node) => node.kind === 'request');
  const seat = nodes.find((node) => node.kind === 'seat');
  const assignment = nodes.find((node) => node.kind === 'assignment');

  if (verb === 'FOCUS' && request) {
    return {
      verb,
      campaign_id: request.raw.campaign_id,
      request_id: request.id,
    };
  }

  if (verb === 'ASSIGN' && request && seat) {
    return {
      verb,
      campaign_id: request.raw.campaign_id,
      request_id: request.id,
      seat_id: seat.id,
    };
  }

  if ((verb === 'RELEASE' || verb === 'RING') && assignment) {
    return {
      verb,
      campaign_id: assignment.raw.campaign_id,
      assignment_id: assignment.id,
    };
  }

  return null;
}

function renderConsequence(field, state, fullGraph) {
  const status = projectionAddressStatus(
    'CONSEQUENCE',
    state.addresses,
    fullGraph,
  );
  if (status.status === 'ADDRESS_NOT_REPRESENTABLE') {
    field.append(
      element(
        'div',
        'ADDRESS NOT REPRESENTABLE HERE · retained: '
          + status.missing.map(addressKey).join(', '),
        'instrument-warning',
      ),
    );
  }

  const graph = visibleGraphForScale(
    fullGraph,
    state.scale,
    state.addresses,
  );
  const selectedKeys = new Set(state.addresses.map(addressKey));
  const mapScroll = element('div', '', 'instrument-map-scroll');
  const map = element('div', '', 'instrument-map');

  const laneBuckets = [[], [], [], []];
  for (const node of graph.nodes) laneBuckets[laneIndex(node.kind)].push(node);
  for (const bucket of laneBuckets) {
    bucket.sort((left, right) => left.key.localeCompare(right.key));
  }

  const xByLane = [35, 305, 575, 845];
  const yStart = 72;
  const yStep = 112;
  const positions = new Map();
  const maxRows = Math.max(1, ...laneBuckets.map((bucket) => bucket.length));
  const height = Math.max(420, yStart + maxRows * yStep + 30);
  map.style.height = String(height) + 'px';

  for (let lane = 0; lane < 4; lane += 1) {
    const label = element('div', laneLabel(lane), 'instrument-map-lane-label');
    label.style.left = String(xByLane[lane]) + 'px';
    map.append(label);

    laneBuckets[lane].forEach((node, index) => {
      const x = xByLane[lane];
      const y = yStart + index * yStep;
      positions.set(node.key, {x, y});

      const button = element('button', '', 'instrument-node');
      button.type = 'button';
      button.dataset.addressKind = node.kind;
      button.dataset.addressId = node.id;
      button.dataset.selected = selectedKeys.has(node.key) ? 'true' : 'false';
      button.style.left = String(x) + 'px';
      button.style.top = String(y) + 'px';
      button.append(
        element(
          'span',
          node.kind.replaceAll('_', ' '),
          'instrument-node-kind',
        ),
        element('strong', node.label),
        element('span', stateFor(node), 'instrument-node-state'),
      );
      map.append(button);
    });
  }

  const svg = svgElement('svg');
  svg.classList.add('instrument-graph-edges');
  svg.setAttribute('viewBox', '0 0 1080 ' + String(height));
  svg.setAttribute('preserveAspectRatio', 'none');
  const defs = svgElement('defs');
  const marker = svgElement('marker');
  marker.setAttribute('id', 'instrument-arrow');
  marker.setAttribute('markerWidth', '8');
  marker.setAttribute('markerHeight', '8');
  marker.setAttribute('refX', '7');
  marker.setAttribute('refY', '3');
  marker.setAttribute('orient', 'auto');
  const path = svgElement('path');
  path.setAttribute('d', 'M0,0 L0,6 L7,3 z');
  marker.append(path);
  defs.append(marker);
  svg.append(defs);

  for (const edge of graph.edges) {
    const source = positions.get(edge.sourceKey);
    const target = positions.get(edge.targetKey);
    if (!source || !target) continue;
    const line = svgElement('line');
    line.setAttribute('x1', String(source.x + 188));
    line.setAttribute('y1', String(source.y + 38));
    line.setAttribute('x2', String(target.x));
    line.setAttribute('y2', String(target.y + 38));
    line.setAttribute('marker-end', 'url(#instrument-arrow)');
    line.classList.add('instrument-graph-edge');
    if (
      selectedKeys.has(edge.sourceKey)
      || selectedKeys.has(edge.targetKey)
    ) {
      line.classList.add('is-selected');
    }
    const title = svgElement('title');
    title.textContent =
      edge.sourceKey + ' —' + edge.relation + '→ ' + edge.targetKey;
    line.append(title);
    svg.append(line);
  }

  map.prepend(svg);
  if (!graph.nodes.length) {
    map.append(
      element(
        'p',
        state.snapshot
          ? 'No objects are visible at this scale.'
          : 'LIVE RUNTIME NOT CONNECTED · consequence objects unavailable.',
        'instrument-map-empty',
      ),
    );
  }

  mapScroll.append(map);
  field.append(mapScroll);

  const relations = element('section', '', 'instrument-relations');
  relations.append(element('h3', 'EXACT RELATIONS AT CURRENT ADDRESS'));
  const active = fullGraph.edges.filter(
    (edge) =>
      selectedKeys.has(edge.sourceKey)
      || selectedKeys.has(edge.targetKey),
  );
  if (!active.length) {
    relations.append(
      element(
        'p',
        'No exact relation projected for current address.',
        'instrument-empty',
      ),
    );
  }
  for (const edge of active) {
    relations.append(
      element(
        'div',
        edge.sourceKey
          + ' —'
          + edge.relation
          + '→ '
          + edge.targetKey,
        'instrument-edge',
      ),
    );
  }
  relations.append(
    element(
      'p',
      'LAYOUT IS NON-SEMANTIC · POSITION / PROXIMITY ≠ RELATION · SCREEN ORDER ≠ PRIORITY · only exact identifiers create edges.',
      'instrument-law',
    ),
  );
  field.append(relations);
}

function renderTopology(field, state, graph) {
  const grid = element('section', '', 'instrument-topology-grid');
  if (!state.addresses.length) {
    grid.append(
      element(
        'p',
        'Select an operational or semantic coordinate to inspect topology. The legacy semantic Atlas remains available below.',
        'instrument-empty',
      ),
    );
  }

  for (const itemAddress of state.addresses) {
    const operationalNode = graph.byKey.get(addressKey(itemAddress));
    const semanticNode = observerAddressObject(
      state.observerModel,
      itemAddress,
    );
    const card = element('article', '', 'instrument-topology-card');
    card.append(
      element(
        'span',
        addressKey(itemAddress),
        'instrument-node-kind',
      ),
      element(
        'h3',
        operationalNode?.label
          || semanticNode?.label
          || String(itemAddress.id),
      ),
    );

    if (!operationalNode && !semanticNode) {
      card.append(
        element(
          'p',
          'Coordinate retained but not present in the currently loaded topology basis.',
          'instrument-warning',
        ),
      );
      grid.append(card);
      continue;
    }

    card.append(element('h4', 'EXPLICIT RELATIONS'));
    if (operationalNode) {
      const edges = graph.edges.filter(
        (edge) =>
          edge.sourceKey === operationalNode.key
          || edge.targetKey === operationalNode.key,
      );
      if (!edges.length) {
        card.append(
          element(
            'p',
            'No exact operational relations projected.',
            'instrument-empty',
          ),
        );
      }
      for (const edge of edges) {
        card.append(
          element(
            'div',
            edge.sourceKey
              + ' —'
              + edge.relation
              + '→ '
              + edge.targetKey,
            'instrument-edge',
          ),
        );
      }
    } else {
      const relations = observerAddressRelations(
        state.observerModel,
        itemAddress,
      );
      if (!relations.length) {
        card.append(
          element(
            'p',
            'No normalized semantic relation projected.',
            'instrument-empty',
          ),
        );
      }
      for (const relation of relations) {
        card.append(
          element(
            'div',
            String(relation.source)
              + ' —'
              + relation.relation
              + '→ '
              + String(relation.target)
              + (relation.ambiguous ? ' [AMBIGUOUS]' : ''),
            'instrument-edge',
          ),
        );
      }
    }

    const raw = operationalNode?.raw || semanticNode?.raw;
    card.append(
      element('h4', 'RAW / PROVENANCE-BEARING OBJECT'),
      element(
        'pre',
        JSON.stringify(raw, null, 2),
        'instrument-raw',
      ),
    );
    grid.append(card);
  }

  grid.append(
    element(
      'p',
      'TOPOLOGY EXPLAINS SUPPORT AND RELATION · OBSERVATION ≠ EVALUATION ≠ AUTHORITY · RAW PRESENCE ≠ STANDING.',
      'instrument-law',
    ),
  );
  field.append(grid);
}

export function createPerceptualInstrument(root) {
  if (!root) return null;

  const params = new URL(window.location.href).searchParams;
  const state = {
    projection: 'CONSEQUENCE',
    scale: 'WORLD',
    addresses: [],
    snapshot: null,
    observerModel: null,
    controlConfigured: Boolean(params.get('control')),
    chatOpen: false,
    chatDraft: '',
    planOpen: false,
    planDraft: '',
  };

  document.body.classList.add('instrument-active');

  const render = () => {
    document.body.dataset.instrumentProjection = state.projection;
    root.replaceChildren();
    root.className = 'perceptual-instrument';

    const header = element('header', '', 'instrument-header');
    const title = element('div');
    title.append(
      element(
        'span',
        'COCKPIT PERCEPTUAL INSTRUMENT',
        'instrument-kicker',
      ),
      element('h1', 'One ecology · two projections'),
    );

    const toggles = element('div', '', 'instrument-toggle');
    for (const projection of PROJECTION_NAMES) {
      const button = element(
        'button',
        projection,
        'instrument-toggle-button',
      );
      button.type = 'button';
      button.dataset.projection = projection;
      button.dataset.active =
        state.projection === projection ? 'true' : 'false';
      toggles.append(button);
    }

    header.append(title, toggles);
    root.append(
      header,
      element(
        'p',
        state.projection === 'CONSEQUENCE'
          ? 'CONSEQUENCE → what is happening / what can I engage'
          : 'TOPOLOGY → what does this mean / what supports it',
        'instrument-law-primary',
      ),
    );

    const scaleBar = element('div', '', 'instrument-scale');
    scaleBar.append(
      element('span', 'SCALE', 'instrument-kicker'),
    );
    for (const scale of SCALE_NAMES) {
      const button = element(
        'button',
        scale.replace('_', ' / '),
        'instrument-scale-button',
      );
      button.type = 'button';
      button.dataset.scale = scale;
      button.dataset.active =
        state.scale === scale ? 'true' : 'false';
      scaleBar.append(button);
    }
    scaleBar.append(
      element(
        'span',
        'ZOOM ≠ PROMOTION · HIDDEN AT CURRENT SCALE ≠ ABSENT',
        'instrument-law',
      ),
    );
    root.append(scaleBar);

    const body = element('div', '', 'instrument-body');
    const field = element('div', '', 'instrument-field');
    const graph = buildOperationalGraph(state.snapshot);

    if (state.projection === 'CONSEQUENCE') {
      renderConsequence(field, state, graph);
    } else {
      renderTopology(field, state, graph);
    }
    body.append(field);

    const rail = element('aside', '', 'instrument-rail');
    rail.append(
      element('span', 'CURRENT ADDRESS', 'instrument-kicker'),
    );
    if (!state.addresses.length) {
      rail.append(
        element('p', 'Nothing selected.', 'instrument-empty'),
      );
    }
    for (const itemAddress of state.addresses) {
      rail.append(
        element(
          'code',
          addressKey(itemAddress),
          'instrument-chip',
        ),
      );
    }

    const actions = element('div', '', 'instrument-actions');
    for (const affordance of deriveContextualAffordances({
      addresses: state.addresses,
      snapshot: state.snapshot,
      controlConfigured: state.controlConfigured,
    })) {
      const button = element(
        'button',
        affordance.verb,
        'instrument-action',
      );
      button.type = 'button';
      button.dataset.action = affordance.verb;
      button.title = affordance.admissibility
        ? affordance.effect + ' · ' + affordance.admissibility
        : affordance.effect;
      actions.append(button);
    }
    rail.append(actions);

    if (state.chatOpen) {
      const packet = buildAddressedChatPacket({
        addresses: state.addresses,
        snapshot: state.snapshot,
        repositoryState: state.observerModel?.repositoryState,
      });
      const box = element('section', '', 'instrument-chat');
      box.append(
        element('h3', 'ADDRESSED CHAT'),
        element(
          'pre',
          JSON.stringify(packet, null, 2),
          'instrument-packet',
        ),
      );

      const area = document.createElement('textarea');
      area.placeholder = 'Talk from this coordinate…';
      area.value = state.chatDraft;
      area.addEventListener('input', () => {
        state.chatDraft = area.value;
      });

      const copy = element(
        'button',
        'COPY ADDRESSED PROMPT',
        'instrument-action',
      );
      copy.type = 'button';
      copy.addEventListener('click', async () => {
        const value =
          '[COCKPIT ADDRESS CONTEXT]\n'
          + JSON.stringify(packet, null, 2)
          + '\n\n[USER MESSAGE]\n'
          + state.chatDraft;
        try {
          await navigator.clipboard.writeText(value);
          copy.textContent = 'COPIED';
        } catch {
          copy.textContent = 'COPY UNAVAILABLE';
        }
      });

      box.append(
        area,
        copy,
        element(
          'p',
          'CHAT TRANSPORT: UNBOUND · address packet has no semantic, authority, or execution effect.',
          'instrument-law',
        ),
      );
      rail.append(box);
    }

    if (state.planOpen) {
      const draft = buildCampaignPlanDraft({
        addresses: state.addresses,
        snapshot: state.snapshot,
        note: state.planDraft,
      });
      const box = element('section', '', 'instrument-plan');
      box.append(element('h3', 'CAMPAIGN PLAN DRAFT'));

      const area = document.createElement('textarea');
      area.value = state.planDraft;
      area.placeholder = 'What should this campaign pressure next?';
      area.addEventListener('input', () => {
        state.planDraft = area.value;
      });

      box.append(
        area,
        element(
          'pre',
          JSON.stringify(draft, null, 2),
          'instrument-packet',
        ),
        element(
          'p',
          'LOCAL DRAFT ONLY · adoption / selection / assignment / priority / authority / execution effects = NONE.',
          'instrument-law',
        ),
      );
      rail.append(box);
    }

    body.append(rail);
    root.append(body);

    root.querySelectorAll('[data-projection]').forEach((button) => {
      button.addEventListener('click', () => {
        state.projection = button.dataset.projection;
        render();
      });
    });

    root.querySelectorAll('[data-scale]').forEach((button) => {
      button.addEventListener('click', () => {
        state.scale = button.dataset.scale;
        render();
      });
    });

    root
      .querySelectorAll('[data-address-kind][data-address-id]')
      .forEach((button) => {
        button.addEventListener('click', (event) => {
          state.addresses = toggleAddressSelection(
            state.addresses,
            address(
              button.dataset.addressKind,
              button.dataset.addressId,
            ),
            event.ctrlKey || event.metaKey || event.shiftKey,
          );
          render();
        });
      });

    root.querySelectorAll('[data-action]').forEach((button) => {
      button.addEventListener('click', () => {
        const verb = button.dataset.action;

        if (verb === 'CHAT') {
          state.chatOpen = !state.chatOpen;
          render();
          return;
        }

        if (verb === 'PLAN') {
          state.planOpen = !state.planOpen;
          render();
          return;
        }

        if (verb === 'COMPARE') return;

        const detail = controlPrefill(
          verb,
          state.addresses,
          state.snapshot,
        );
        if (detail) {
          window.dispatchEvent(
            new CustomEvent('cockpit-control-prefill', {detail}),
          );
        }
      });
    });
  };

  render();

  return {
    setRuntimeSnapshot(snapshot) {
      state.snapshot = snapshot;
      render();
    },
    setObserverModel(model) {
      state.observerModel = model;
      render();
    },
    selectAddress(kind, id, additive = false) {
      state.addresses = toggleAddressSelection(
        state.addresses,
        address(kind, id),
        additive,
      );
      state.projection = 'TOPOLOGY';
      render();
    },
    currentState() {
      return {
        projection: state.projection,
        scale: state.scale,
        addresses: structuredClone(state.addresses),
        runtime_state_sha256:
          state.snapshot?.state_sha256 || null,
      };
    },
  };
}
