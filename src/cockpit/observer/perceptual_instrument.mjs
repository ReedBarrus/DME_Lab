export const PROJECTION_NAMES = Object.freeze(['CONSEQUENCE', 'TOPOLOGY']);
const array = (value) => Array.isArray(value) ? value : [];
const objects = (rows, field) => array(rows).map((row) => row && row[field]).filter((value) => value && typeof value === 'object');
export const addressKey = (address) => address && address.kind && address.id != null ? String(address.kind) + ':' + String(address.id) : '';
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
  const state = snapshot && snapshot.state ? snapshot.state : {};
  const nodes = [];
  const edges = [];
  const byKey = new Map();
  const addNode = (kind, id, label, raw, meta = {}) => {
    if (!id) return;
    const itemAddress = address(kind, id);
    const key = addressKey(itemAddress);
    if (byKey.has(key)) return;
    const node = {key, address: itemAddress, kind, id: String(id), label: label || String(id), raw, meta};
    nodes.push(node);
    byKey.set(key, node);
  };
  const addEdge = (source, target, relation) => {
    const sourceKey = addressKey(source);
    const targetKey = addressKey(target);
    if (!byKey.has(sourceKey) || !byKey.has(targetKey)) return;
    if (edges.some((edge) => edge.sourceKey === sourceKey && edge.targetKey === targetKey && edge.relation === relation)) return;
    edges.push({source, target, sourceKey, targetKey, relation});
  };
  const horizons = new Map(array(state.development_horizons && state.development_horizons.horizons).map((item) => [item.campaign_id, item]));
  for (const row of array(state.campaigns)) {
    const campaign = row && row.campaign_json;
    if (campaign && campaign.campaign_id) addNode('campaign', campaign.campaign_id, campaign.title || campaign.campaign_id, campaign, {horizon_state: (horizons.get(campaign.campaign_id) || {}).horizon_state || 'UNPROJECTED'});
  }
  const selected = new Set(array(state.current_selection).map((item) => item && item.request_id).filter(Boolean));
  for (const request of objects(state.requests, 'request_json')) {
    if (request.request_id) addNode('request', request.request_id, request.title || request.relation_id || request.request_id, request, {selected: selected.has(request.request_id)});
  }
  for (const seat of array(state.seats)) {
    if (seat && seat.seat_id) addNode('seat', seat.seat_id, seat.seat_id, seat, {occupancy_state: seat.occupancy_state || 'UNKNOWN'});
  }
  for (const assignment of outstandingAssignments(state)) addNode('assignment', assignment.assignment_id, assignment.assignment_id, assignment, {assignment_state: 'OUTSTANDING'});
  for (const bell of objects(state.manual_bells, 'bell_json')) {
    const id = bell.bell_id || bell.manual_bell_id;
    if (id) addNode('bell', id, id, bell);
  }
  for (const wake of objects(state.reentry_opportunities, 'opportunity_json')) {
    if (wake.opportunity_id) addNode('wake', wake.opportunity_id, wake.opportunity_id, wake);
  }
  for (const pair of [['preparation_receipt', state.preparation_receipts], ['reentry_receipt', state.reentry_receipts], ['execution_receipt', state.execution_receipts]]) {
    for (const receipt of objects(pair[1], 'receipt_json')) {
      const id = receipt.receipt_id || receipt.preparation_id || receipt.execution_receipt_id;
      if (id) addNode(pair[0], id, id, receipt);
    }
  }
  for (const lease of array(state.active_model_leases)) {
    if (lease && lease.lease_id) addNode('model_lease', lease.lease_id, lease.resource_id || lease.lease_id, lease);
  }
  for (const node of nodes) {
    const raw = node.raw || {};
    if (node.kind === 'request' && raw.campaign_id) addEdge(address('campaign', raw.campaign_id), node.address, 'declares_request');
    if (node.kind === 'assignment') {
      if (raw.request_id) addEdge(address('request', raw.request_id), node.address, 'assigned_as');
      if (raw.seat_id) addEdge(address('seat', raw.seat_id), node.address, 'assigned_to');
    }
    if (node.kind === 'bell' && raw.assignment_id) addEdge(address('assignment', raw.assignment_id), node.address, 'rings');
    if (node.kind === 'wake') {
      if (raw.assignment_id) addEdge(address('assignment', raw.assignment_id), node.address, 'permits_wake_opportunity');
      if (raw.seat_id) addEdge(address('seat', raw.seat_id), node.address, 'wake_for');
    }
    if (node.kind.endsWith('receipt')) {
      if (raw.request_id) addEdge(address('request', raw.request_id), node.address, 'has_receipt');
      if (raw.opportunity_id) addEdge(address('wake', raw.opportunity_id), node.address, 'has_receipt');
    }
    if (node.kind === 'model_lease' && raw.seat_id) addEdge(address('seat', raw.seat_id), node.address, 'leases_model');
  }
  return {nodes, edges, byKey, snapshot_sha256: snapshot && snapshot.state_sha256 || null};
}

export function toggleAddressSelection(current, next, additive = false) {
  const key = addressKey(next);
  const existing = array(current);
  if (!key) return existing;
  if (!additive) return [next];
  return existing.some((item) => addressKey(item) === key) ? existing.filter((item) => addressKey(item) !== key) : existing.concat([next]);
}

export function projectionAddressStatus(projection, addresses, graph) {
  const selected = array(addresses);
  if (!selected.length) return {status: 'EMPTY', missing: []};
  if (projection === 'TOPOLOGY') return {status: 'REPRESENTABLE', missing: []};
  const missing = selected.filter((item) => !graph || !graph.byKey.has(addressKey(item)));
  return {status: missing.length ? 'ADDRESS_NOT_REPRESENTABLE' : 'REPRESENTABLE', missing};
}

export function buildAddressedChatPacket({addresses, snapshot, repositoryState}) {
  return {
    schema: 'cockpit_address_context_v0',
    addresses: array(addresses).map((item) => ({kind: item.kind, id: String(item.id)})),
    runtime_state_sha256: snapshot && snapshot.state_sha256 || null,
    repository_source_commit: repositoryState && repositoryState.source_commit || null,
    repository_source_ref: repositoryState && repositoryState.source_ref || null,
    authority_effect: 'NONE', semantic_claim_effect: 'NONE', transport_effect: 'NONE'
  };
}

export function deriveContextualAffordances({addresses, snapshot, controlConfigured = false}) {
  const graph = buildOperationalGraph(snapshot);
  const selectedNodes = array(addresses).map((item) => graph.byKey.get(addressKey(item))).filter(Boolean);
  const byKind = (kind) => selectedNodes.filter((node) => node.kind === kind);
  const result = [];
  if (array(addresses).length) result.push({verb: 'CHAT', effect: 'LOCAL_CONTEXT_ONLY'});
  if (array(addresses).length > 1) result.push({verb: 'COMPARE', effect: 'LOCAL_VIEW_ONLY'});
  if (byKind('campaign').length === 1) result.push({verb: 'PLAN', effect: 'LOCAL_DRAFT_ONLY'});
  if (!controlConfigured) return result;
  const selectedRequests = new Set(array(snapshot && snapshot.state && snapshot.state.current_selection).map((item) => item && item.request_id).filter(Boolean));
  if (byKind('request').length === 1 && !selectedRequests.has(byKind('request')[0].id)) result.push({verb: 'FOCUS', effect: 'QUALIFIED_CONTROL_PREVIEW'});
  if (byKind('request').length === 1 && byKind('seat').length === 1 && selectedRequests.has(byKind('request')[0].id)) result.push({verb: 'ASSIGN', effect: 'QUALIFIED_CONTROL_PREVIEW'});
  if (byKind('assignment').length === 1) result.push({verb: 'RELEASE', effect: 'QUALIFIED_CONTROL_PREVIEW'}, {verb: 'RING', effect: 'QUALIFIED_CONTROL_PREVIEW'});
  return result;
}

export function buildCampaignPlanDraft({addresses, snapshot, note = ''}) {
  const graph = buildOperationalGraph(snapshot);
  const campaign = array(addresses).map((item) => graph.byKey.get(addressKey(item))).find((node) => node && node.kind === 'campaign');
  if (!campaign) return null;
  return {schema: 'cockpit_campaign_plan_draft_v0', campaign_id: campaign.id, source_runtime_state_sha256: snapshot && snapshot.state_sha256 || null, note, adoption_effect: 'NONE', selection_effect: 'NONE', assignment_effect: 'NONE', authority_effect: 'NONE', execution_effect: 'NONE'};
}

const element = (tag, text = '', className = '') => { const node = document.createElement(tag); if (text) node.textContent = text; if (className) node.className = className; return node; };
function groupFor(kind) { if (kind === 'campaign') return 'CAMPAIGNS'; if (kind === 'seat' || kind === 'model_lease') return 'SEATS / MODELS'; if (['request','assignment','bell','wake'].includes(kind)) return 'CONSEQUENCE FLOW'; return 'RECEIPTS'; }
function stateFor(node) { if (node.kind === 'campaign') return node.meta.horizon_state || 'UNPROJECTED'; if (node.kind === 'request') return node.meta.selected ? 'SELECTED' : 'AVAILABLE'; if (node.kind === 'seat') return node.meta.occupancy_state || 'UNKNOWN'; if (node.kind === 'assignment') return 'OUTSTANDING'; return node.kind.replaceAll('_',' ').toUpperCase(); }
function controlPrefill(verb, addresses, snapshot) { const graph = buildOperationalGraph(snapshot); const nodes = addresses.map((item) => graph.byKey.get(addressKey(item))).filter(Boolean); const request = nodes.find((node) => node.kind === 'request'); const seat = nodes.find((node) => node.kind === 'seat'); const assignment = nodes.find((node) => node.kind === 'assignment'); if (verb === 'FOCUS' && request) return {verb, campaign_id: request.raw.campaign_id, request_id: request.id}; if (verb === 'ASSIGN' && request && seat) return {verb, campaign_id: request.raw.campaign_id, request_id: request.id, seat_id: seat.id}; if ((verb === 'RELEASE' || verb === 'RING') && assignment) return {verb, campaign_id: assignment.raw.campaign_id, assignment_id: assignment.id}; return null; }

export function createPerceptualInstrument(root) {
  if (!root) return null;
  const params = new URL(window.location.href).searchParams;
  const state = {projection: 'CONSEQUENCE', addresses: [], snapshot: null, observerModel: null, controlConfigured: Boolean(params.get('control')), chatOpen: false, chatDraft: '', planOpen: false, planDraft: ''};
  document.body.classList.add('instrument-active');
  const render = () => {
    document.body.dataset.instrumentProjection = state.projection;
    root.replaceChildren(); root.className = 'perceptual-instrument';
    const header = element('header', '', 'instrument-header');
    const title = element('div'); title.append(element('span','COCKPIT PERCEPTUAL INSTRUMENT','instrument-kicker'), element('h1','One ecology · two projections'));
    const toggles = element('div', '', 'instrument-toggle');
    for (const projection of PROJECTION_NAMES) { const button = element('button', projection, 'instrument-toggle-button'); button.type = 'button'; button.dataset.projection = projection; button.dataset.active = state.projection === projection ? 'true' : 'false'; toggles.append(button); }
    header.append(title, toggles); root.append(header, element('p', state.projection === 'CONSEQUENCE' ? 'CONSEQUENCE → what is happening / what can I engage' : 'TOPOLOGY → what does this mean / what supports it', 'instrument-law-primary'));
    const body = element('div', '', 'instrument-body'); const field = element('div', '', 'instrument-field'); const graph = buildOperationalGraph(state.snapshot); const selectedKeys = new Set(state.addresses.map(addressKey));
    if (state.projection === 'CONSEQUENCE') {
      const status = projectionAddressStatus('CONSEQUENCE', state.addresses, graph); if (status.status === 'ADDRESS_NOT_REPRESENTABLE') field.append(element('div', 'ADDRESS NOT REPRESENTABLE HERE · retained: ' + status.missing.map(addressKey).join(', '), 'instrument-warning'));
      const world = element('div', '', 'instrument-world');
      for (const group of ['CAMPAIGNS','SEATS / MODELS','CONSEQUENCE FLOW','RECEIPTS']) { const lane = element('section','', 'instrument-lane'); lane.append(element('h3', group)); const nodes = graph.nodes.filter((node) => groupFor(node.kind) === group); if (!nodes.length) lane.append(element('p','No projected objects.','instrument-empty')); for (const node of nodes) { const button = element('button','', 'instrument-node'); button.type='button'; button.dataset.addressKind=node.kind; button.dataset.addressId=node.id; button.dataset.selected=selectedKeys.has(node.key)?'true':'false'; button.append(element('span',node.kind.replaceAll('_',' '),'instrument-node-kind'),element('strong',node.label),element('span',stateFor(node),'instrument-node-state')); lane.append(button); } world.append(lane); }
      field.append(world); const relations = element('section','', 'instrument-relations'); relations.append(element('h3','EXPLICIT RELATIONS')); const active = graph.edges.filter((edge) => selectedKeys.has(edge.sourceKey) || selectedKeys.has(edge.targetKey)); if (!active.length) relations.append(element('p','No exact relation projected for current address.','instrument-empty')); for (const edge of active) relations.append(element('div', edge.sourceKey + ' —' + edge.relation + '→ ' + edge.targetKey, 'instrument-edge')); relations.append(element('p','POSITION / PROXIMITY ≠ RELATION · only explicit identifiers create edges.','instrument-law')); field.append(relations);
    } else {
      const grid = element('section','', 'instrument-topology-grid'); if (!state.addresses.length) grid.append(element('p','Select an operational coordinate to inspect topology.','instrument-empty')); for (const itemAddress of state.addresses) { const node = graph.byKey.get(addressKey(itemAddress)); const card = element('article','', 'instrument-topology-card'); card.append(element('span',addressKey(itemAddress),'instrument-node-kind'),element('h3',node ? node.label : String(itemAddress.id))); if (!node) card.append(element('p','Coordinate retained but not present in currently loaded operational basis.','instrument-warning')); else { const edges = graph.edges.filter((edge) => edge.sourceKey === node.key || edge.targetKey === node.key); card.append(element('h4','EXPLICIT RELATIONS')); if (!edges.length) card.append(element('p','No exact operational relations projected.','instrument-empty')); for (const edge of edges) card.append(element('div',edge.sourceKey + ' —' + edge.relation + '→ ' + edge.targetKey,'instrument-edge')); card.append(element('h4','RAW / PROVENANCE-BEARING OBJECT'), element('pre',JSON.stringify(node.raw,null,2),'instrument-raw')); } grid.append(card); } grid.append(element('p','TOPOLOGY EXPLAINS SUPPORT AND RELATION · RAW PRESENCE ≠ STANDING OR AUTHORITY.','instrument-law')); field.append(grid);
    }
    body.append(field);
    const rail = element('aside','', 'instrument-rail'); rail.append(element('span','CURRENT ADDRESS','instrument-kicker')); if (!state.addresses.length) rail.append(element('p','Nothing selected.','instrument-empty')); for (const itemAddress of state.addresses) rail.append(element('code',addressKey(itemAddress),'instrument-chip'));
    const actions = element('div','', 'instrument-actions'); for (const affordance of deriveContextualAffordances({addresses: state.addresses, snapshot: state.snapshot, controlConfigured: state.controlConfigured})) { const button = element('button',affordance.verb,'instrument-action'); button.type='button'; button.dataset.action=affordance.verb; button.title=affordance.effect; actions.append(button); } rail.append(actions);
    if (state.chatOpen) { const packet = buildAddressedChatPacket({addresses:state.addresses,snapshot:state.snapshot,repositoryState:state.observerModel && state.observerModel.repositoryState}); const box=element('section','', 'instrument-chat'); box.append(element('h3','ADDRESSED CHAT'),element('pre',JSON.stringify(packet,null,2),'instrument-packet')); const area=document.createElement('textarea'); area.placeholder='Talk from this coordinate…'; area.value=state.chatDraft; area.addEventListener('input',()=>state.chatDraft=area.value); const copy=element('button','COPY ADDRESSED PROMPT','instrument-action'); copy.type='button'; copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText('[COCKPIT ADDRESS CONTEXT]\n'+JSON.stringify(packet,null,2)+'\n\n[USER MESSAGE]\n'+state.chatDraft);copy.textContent='COPIED';}catch{copy.textContent='COPY UNAVAILABLE';}}); box.append(area,copy,element('p','CHAT TRANSPORT: UNBOUND · packet has no authority or execution effect.','instrument-law')); rail.append(box); }
    if (state.planOpen) { const draft=buildCampaignPlanDraft({addresses:state.addresses,snapshot:state.snapshot,note:state.planDraft}); const box=element('section','', 'instrument-plan'); box.append(element('h3','CAMPAIGN PLAN DRAFT')); const area=document.createElement('textarea'); area.value=state.planDraft; area.placeholder='What should this campaign pressure next?'; area.addEventListener('input',()=>state.planDraft=area.value); box.append(area,element('pre',JSON.stringify(draft,null,2),'instrument-packet'),element('p','LOCAL DRAFT ONLY · effects = NONE.','instrument-law')); rail.append(box); }
    body.append(rail); root.append(body);
    root.querySelectorAll('[data-projection]').forEach((button)=>button.addEventListener('click',()=>{state.projection=button.dataset.projection;render();}));
    root.querySelectorAll('[data-address-kind][data-address-id]').forEach((button)=>button.addEventListener('click',(event)=>{state.addresses=toggleAddressSelection(state.addresses,address(button.dataset.addressKind,button.dataset.addressId),event.ctrlKey||event.metaKey||event.shiftKey);render();}));
    root.querySelectorAll('[data-action]').forEach((button)=>button.addEventListener('click',()=>{const verb=button.dataset.action;if(verb==='CHAT'){state.chatOpen=!state.chatOpen;render();return;}if(verb==='PLAN'){state.planOpen=!state.planOpen;render();return;}if(verb==='COMPARE')return;const detail=controlPrefill(verb,state.addresses,state.snapshot);if(detail)window.dispatchEvent(new CustomEvent('cockpit-control-prefill',{detail}));}));
  };
  render();
  return {setRuntimeSnapshot(snapshot){state.snapshot=snapshot;render();},setObserverModel(model){state.observerModel=model;render();},currentState(){return{projection:state.projection,addresses:structuredClone(state.addresses),runtime_state_sha256:state.snapshot&&state.snapshot.state_sha256||null};}};
}
