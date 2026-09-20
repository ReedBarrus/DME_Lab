import assert from 'node:assert/strict';
import test from 'node:test';
import {
  PROJECTION_NAMES,
  addressKey,
  buildOperationalGraph,
  toggleAddressSelection,
  projectionAddressStatus,
  buildAddressedChatPacket,
  deriveContextualAffordances,
  buildCampaignPlanDraft,
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
  assert.equal(projectionAddressStatus('TOPOLOGY', semanticOnly, graph).status, 'REPRESENTABLE');
  const consequence = projectionAddressStatus('CONSEQUENCE', semanticOnly, graph);
  assert.equal(consequence.status, 'ADDRESS_NOT_REPRESENTABLE');
  assert.deepEqual(consequence.missing, semanticOnly);
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
