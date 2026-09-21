import assert from 'node:assert/strict';
import test from 'node:test';
import {
  PROJECTION_NAMES,
  SCALE_NAMES,
  addressKey,
  buildOperationalGraph,
  toggleAddressSelection,
  projectionAddressStatus,
  buildAddressedChatPacket,
  deriveContextualAffordances,
  buildCampaignPlanDraft,
  visibleGraphForScale,
  observerAddressObject,
  observerAddressRelations,
} from '../../src/cockpit/observer/perceptual_instrument.mjs';

function snapshot() {
  return {
    state_sha256: 's'.repeat(64),
    state: {
      campaigns: [{campaign_json:{campaign_id:'C1',title:'Campaign One'}}],
      development_horizons: {horizons:[{campaign_id:'C1',horizon_state:'ACTIVE'}]},
      requests: [{request_json:{campaign_id:'C1',request_id:'R1',relation_id:'REL1'}}],
      current_selection: [],
      seats: [{seat_id:'MAYA',occupancy_state:'AVAILABLE'}],
      assignment_history: [],
      assignment_satisfactions: [],
      manual_bells: [],
      reentry_opportunities: [],
      preparation_receipts: [],
      reentry_receipts: [],
      execution_receipts: [],
      active_model_leases: [],
    },
  };
}

test('primary projections are consequence and topology only', () => {
  assert.deepEqual(PROJECTION_NAMES, ['CONSEQUENCE','TOPOLOGY']);
});

test('operational graph derives only explicit identifier relations', () => {
  const graph = buildOperationalGraph(snapshot());
  assert.ok(graph.byKey.has('campaign:C1'));
  assert.ok(graph.byKey.has('request:R1'));
  assert.ok(graph.byKey.has('seat:MAYA'));
  assert.deepEqual(graph.edges.map((edge) => [edge.sourceKey,edge.relation,edge.targetKey]), [
    ['campaign:C1','declares_request','request:R1'],
  ]);
});

test('address persists across projections and missing consequence representation is explicit', () => {
  const graph = buildOperationalGraph(snapshot());
  const semanticOnly = [{kind:'pressure_occurrence',id:'PR-001'}];
  const observer = {
    occurrences:[{key:'PR-001',node:{id:'PR-001',title:'Pressure one'}}],
    constraintOccurrences:[],
    evidenceOccurrences:[],
    projectionDocumentOccurrences:[],
  };
  assert.equal(
    projectionAddressStatus('TOPOLOGY', semanticOnly, graph, observer).status,
    'REPRESENTABLE',
  );
  const consequence = projectionAddressStatus('CONSEQUENCE', semanticOnly, graph, observer);
  assert.equal(consequence.status, 'ADDRESS_NOT_REPRESENTABLE');
  assert.deepEqual(consequence.missing, semanticOnly);
});

test('topology representability follows exact loaded basis presence', () => {
  const graph = buildOperationalGraph(snapshot());
  const observer = {
    occurrences:[{
      key:'P1-exact',
      node:{id:'P1-exact',title:'Exact pressure'},
    }],
    constraintOccurrences:[],
    evidenceOccurrences:[],
    projectionDocumentOccurrences:[],
  };

  const t1 = [{kind:'pressure_occurrence',id:'P1-exact'}];
  const t2 = [{kind:'pressure_occurrence',id:'P1-absent'}];
  const t3 = [{kind:'request',id:'R1'}];
  const t4 = [{kind:'request',id:'R-missing'}];

  assert.deepEqual(
    projectionAddressStatus('TOPOLOGY', t1, graph, observer),
    {status:'REPRESENTABLE',missing:[]},
  );
  assert.deepEqual(
    projectionAddressStatus('TOPOLOGY', t2, graph, observer),
    {status:'ADDRESS_NOT_REPRESENTABLE',missing:t2},
  );
  assert.deepEqual(
    projectionAddressStatus('TOPOLOGY', t3, graph, observer),
    {status:'REPRESENTABLE',missing:[]},
  );
  assert.deepEqual(
    projectionAddressStatus('TOPOLOGY', t4, graph, observer),
    {status:'ADDRESS_NOT_REPRESENTABLE',missing:t4},
  );
});

test('multi-selection never implies priority', () => {
  let selected = toggleAddressSelection([], {kind:'request',id:'R1'});
  selected = toggleAddressSelection(selected, {kind:'seat',id:'MAYA'}, true);
  assert.deepEqual(selected, [{kind:'request',id:'R1'},{kind:'seat',id:'MAYA'}]);
  assert.deepEqual(selected.map(addressKey), ['request:R1','seat:MAYA']);
});

test('addressed chat packet is local context without authority or transport', () => {
  const packet = buildAddressedChatPacket({
    addresses:[{kind:'request',id:'R1'}],
    snapshot:snapshot(),
    repositoryState:{source_commit:'abc',source_ref:'HEAD'},
  });
  assert.equal(packet.authority_effect,'NONE');
  assert.equal(packet.semantic_claim_effect,'NONE');
  assert.equal(packet.transport_effect,'NONE');
  assert.deepEqual(packet.addresses,[{kind:'request',id:'R1'}]);
});

test('control affordances require both configured control and exact coordinates', () => {
  let actions = deriveContextualAffordances({
    addresses:[{kind:'request',id:'R1'}],
    snapshot:snapshot(),
    controlConfigured:false,
  });
  assert.deepEqual(actions.map((item)=>item.verb),['CHAT']);
  actions = deriveContextualAffordances({
    addresses:[{kind:'request',id:'R1'}],
    snapshot:snapshot(),
    controlConfigured:true,
  });
  assert.deepEqual(actions.map((item)=>item.verb),['CHAT','FOCUS']);

  const selected = snapshot();
  selected.state.current_selection = [{campaign_id:'C1',request_id:'R1'}];
  actions = deriveContextualAffordances({
    addresses:[{kind:'request',id:'R1'},{kind:'seat',id:'MAYA'}],
    snapshot:selected,
    controlConfigured:true,
  });
  assert.deepEqual(actions.map((item)=>item.verb),['CHAT','COMPARE','ASSIGN']);
});

test('control affordances are prefill candidates, not admissibility claims', () => {
  const state = snapshot();
  state.state.current_selection = [{campaign_id:'C1',request_id:'R1'}];
  state.state.assignment_history = [{
    event_json:{
      assignment_id:'A-DRAFT',
      assignment_kind:'ASSIGNED',
      campaign_id:'C1',
      request_id:'R1',
      seat_id:'MAYA',
      preparation_kind:'DRAFT_PACKET',
    },
  }];

  const actions = deriveContextualAffordances({
    addresses:[{kind:'assignment',id:'A-DRAFT'}],
    snapshot:state,
    controlConfigured:true,
  });

  const control = actions.filter((item)=>['RELEASE','RING'].includes(item.verb));
  assert.deepEqual(control, [
    {
      verb:'RELEASE',
      effect:'CONTROL_PREFILL_ONLY',
      admissibility:'UNVERIFIED_UNTIL_EXACT_PREVIEW',
    },
    {
      verb:'RING',
      effect:'CONTROL_PREFILL_ONLY',
      admissibility:'UNVERIFIED_UNTIL_EXACT_PREVIEW',
    },
  ]);
});

test('campaign planning remains a local draft with zero consequence effects', () => {
  const draft = buildCampaignPlanDraft({
    addresses:[{kind:'campaign',id:'C1'}],
    snapshot:snapshot(),
    note:'pressure R1',
  });
  assert.equal(draft.campaign_id,'C1');
  assert.equal(draft.adoption_effect,'NONE');
  assert.equal(draft.selection_effect,'NONE');
  assert.equal(draft.assignment_effect,'NONE');
  assert.equal(draft.authority_effect,'NONE');
  assert.equal(draft.execution_effect,'NONE');
});


test('scale filtering preserves selected coordinates without inventing priority', () => {
  const graph = buildOperationalGraph(snapshot());
  const objectView = visibleGraphForScale(
    graph,
    'OBJECT',
    [{kind:'request',id:'R1'}],
  );
  assert.ok(objectView.nodes.some((node)=>node.key === 'request:R1'));
  assert.ok(objectView.nodes.some((node)=>node.key === 'campaign:C1'));
  assert.equal(objectView.nodes.some((node)=>node.meta?.priority), false);
  assert.deepEqual(SCALE_NAMES, ['WORLD','CAMPAIGN','SEAT_PROCESS','OBJECT']);
});

test('semantic observer coordinates are exact topology addresses, not nearby substitutions', () => {
  const observer = {
    occurrences:[{
      key:'pressure-001-PR-1-line-10',
      node:{id:'PR-1',title:'Pressure one'},
    }],
    constraintOccurrences:[],
    evidenceOccurrences:[],
    projectionDocumentOccurrences:[],
    semanticEdges:[{
      relation:{relation_kind:'blocked_by'},
      sourceCandidates:[{key:'pressure-001-PR-1-line-10'}],
      targetCandidates:[{key:'pressure-002-PR-2-line-20'}],
      drawable:true,
      ambiguous:false,
    }],
  };
  const exact = {kind:'pressure_occurrence',id:'pressure-001-PR-1-line-10'};
  assert.equal(observerAddressObject(observer, exact).label, 'Pressure one');
  assert.equal(
    observerAddressObject(observer, {kind:'pressure_occurrence',id:'PR-1'}),
    null,
  );
  assert.deepEqual(observerAddressRelations(observer, exact), [{
    relation:'blocked_by',
    source:'pressure-001-PR-1-line-10',
    target:'pressure-002-PR-2-line-20',
    drawable:true,
    ambiguous:false,
  }]);
});
