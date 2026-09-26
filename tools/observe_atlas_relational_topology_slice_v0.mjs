#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {
  classifyAtlasRelationalTopologySlice,
  reconstructAtlasRelationalTopologySlice,
} from '../src/cockpit/observer/atlas_relational_topology_slice.mjs';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const OUT = path.join(
  ROOT,
  'docs',
  'evidence',
  'for_planner',
  'atlas_relational_topology_slice_v0_observation.json',
);

const SPECIMEN_PATH = path.join(
  ROOT,
  'docs',
  'campaigns',
  'atlas_relational_integration_001',
  'specimens',
  'ATLAS_RELATIONAL_TOPOLOGY_SLICE_V0.json',
);

const EXPECTED_BLOBS = {
  planner_result: [
    'docs/campaigns/chatgpt_main_planner_role_001/pressure_runs/CHATGPT_MAIN_ATLAS_PLANNER_ROLE_V0_PRESSURE_RESULT_001.md',
    '67359516883662ad5ef02c5db71e279cc148bad4',
  ],
  h1_adjudication: [
    'docs/campaigns/relational_invariance_load_001/pressure_runs/RELATIONAL_INVARIANCE_LOAD_V0_ADJUDICATION_RESULT_001.md',
    'd0fa23ee2301024e9a6b96dede95ec62b253156f',
  ],
  h2_adjudication: [
    'docs/campaigns/relational_topology_load_001/pressure_runs/RELATIONAL_TOPOLOGY_LOAD_V0_ADJUDICATION_RESULT_001.md',
    'fc789514c9276f3857add4fe90402553d70b441d',
  ],
  atlas_geometry: [
    'src/cockpit/observer/repository_fabric_geometry.mjs',
    'b2b8ccdd3854c15f586c1af609847a1baf655977',
  ],
  atlas_model: [
    'src/cockpit/observer/repository_fabric_model.mjs',
    'e13e50e410f8bd72cf26ce8d9cfce1a6f90cdd44',
  ],
  atlas_app: [
    'src/cockpit/observer/repository_fabric_app.mjs',
    '81ac50e6858ad7fac44cc2e59ea964d0c71705ad',
  ],
  slice_model: [
    'src/cockpit/observer/atlas_relational_topology_slice.mjs',
    '785a108cb454c67d9fc0887e87fbcd1e9a9a4393',
  ],
  slice_specimen: [
    'docs/campaigns/atlas_relational_integration_001/specimens/ATLAS_RELATIONAL_TOPOLOGY_SLICE_V0.json',
    '56b17fbddade245af29175e34e9301ea176252da',
  ],
  horizon: [
    'docs/campaigns/atlas_relational_integration_001/HORIZON_SELECTION_ARI1_V0.md',
    '2e4196d297c8837dd30ad39d6b71522bfdef947e',
  ],
  contract: [
    'docs/campaigns/atlas_relational_integration_001/ARI1_CONTRACT_V0.md',
    '4a28d09c9c5d7b52031afcdbe485913facb2a4e7',
  ],
};

function gitBlob(relativePath) {
  const result = spawnSync(
    'git',
    ['-C', ROOT, 'rev-parse', `HEAD:${relativePath}`],
    {encoding: 'utf8'},
  );
  if (result.status !== 0) {
    throw new Error(`git blob lookup failed for ${relativePath}: ${result.stderr}`);
  }
  return result.stdout.trim();
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function runVariant(id, source) {
  const reconstruction = reconstructAtlasRelationalTopologySlice(source);
  return {
    variant_id: id,
    classification: classifyAtlasRelationalTopologySlice(source),
    reconstruction,
  };
}

if (fs.existsSync(OUT)) {
  throw new Error(`remove existing ${path.relative(ROOT, OUT)} first`);
}

const actualBlobs = Object.fromEntries(
  Object.entries(EXPECTED_BLOBS).map(([name, [relativePath]]) => [
    name,
    gitBlob(relativePath),
  ]),
);
const blobChecks = Object.fromEntries(
  Object.entries(EXPECTED_BLOBS).map(([name, [, expected]]) => [
    name,
    actualBlobs[name] === expected,
  ]),
);
if (!Object.values(blobChecks).every(Boolean)) {
  throw new Error(`frozen blob mismatch: ${JSON.stringify(blobChecks)}`);
}

const specimen = JSON.parse(fs.readFileSync(SPECIMEN_PATH, 'utf8'));

const control = runVariant('S0_CONTROL', specimen);

const flatten = clone(specimen);
delete flatten.local_relation;
flatten.surrounding_topology = {
  relation_ids: ['FOCAL', 'CONTEXT'],
  relation_role: 'UNDIFFERENTIATED_RELATION_BAG',
  note: 'Ablation merges local and surrounding roles.',
};
const a1 = runVariant('A1_FLATTEN_LOCAL_INTO_TOPOLOGY', flatten);

const noSurrounding = clone(specimen);
delete noSurrounding.surrounding_topology;
const a2 = runVariant('A2_REMOVE_SURROUNDING_TOPOLOGY', noSurrounding);

const noGap = clone(specimen);
delete noGap.represented_vs_qualified_gap;
const a3 = runVariant('A3_REMOVE_REPRESENTED_QUALIFIED_GAP', noGap);

const closedExterior = clone(specimen);
closedExterior.unresolved_exterior.status = 'CLOSED';
closedExterior.unresolved_exterior.statement =
  'Ablation claims no unresolved exterior without new evidence.';
const a4 = runVariant('A4_CLOSE_UNRESOLVED_EXTERIOR', closedExterior);

const operativeWorld = clone(specimen);
operativeWorld.projection_status = 'OPERATIVE_WORLD';
const a5 = runVariant('A5_DECLARE_PROJECTION_OPERATIVE_WORLD', operativeWorld);

const variants = [a1, a2, a3, a4, a5];

const expected = {
  S0_CONTROL: 'BOUNDED_SLICE_READY',
  A1_FLATTEN_LOCAL_INTO_TOPOLOGY: 'HOLD_LOCAL_RELATION_LOST',
  A2_REMOVE_SURROUNDING_TOPOLOGY: 'HOLD_SURROUNDING_TOPOLOGY_LOST',
  A3_REMOVE_REPRESENTED_QUALIFIED_GAP: 'HOLD_TOPOLOGY_GAP_LOST',
  A4_CLOSE_UNRESOLVED_EXTERIOR: 'HOLD_UNRESOLVED_EXTERIOR_LOST',
  A5_DECLARE_PROJECTION_OPERATIVE_WORLD: 'HOLD_PROJECTION_WORLD_COLLAPSE',
};

const observed = Object.fromEntries(
  [control, ...variants].map((item) => [item.variant_id, item.classification]),
);

const expectationChecks = Object.fromEntries(
  Object.entries(expected).map(([id, expectedClassification]) => [
    id,
    observed[id] === expectedClassification,
  ]),
);

const controlChecks = control.reconstruction.checks;

const observation = {
  object_type: 'ATLAS_RELATIONAL_TOPOLOGY_SLICE_V0_OBSERVATION',
  pressure_id: 'ATLAS_RELATIONAL_TOPOLOGY_SLICE_V0_PRESSURE_001',
  frozen_basis: {
    expected_blobs: Object.fromEntries(
      Object.entries(EXPECTED_BLOBS).map(([name, [, expectedBlob]]) => [
        name,
        expectedBlob,
      ]),
    ),
    actual_blobs: actualBlobs,
    blob_checks: blobChecks,
  },
  cases: {
    control,
    variants,
  },
  observed_classifications: observed,
  expectation_checks: expectationChecks,
  all_expectations_match: Object.values(expectationChecks).every(Boolean),
  control_coordinates: {
    local_relation_preserved: controlChecks.local_relation_recoverable,
    surrounding_topology_preserved:
      controlChecks.surrounding_topology_recoverable,
    represented_topology_preserved:
      controlChecks.represented_topology_recoverable,
    qualified_specimen_topology_preserved:
      controlChecks.qualified_specimen_topology_recoverable,
    represented_vs_qualified_gap_preserved:
      controlChecks.represented_vs_qualified_gap_recoverable,
    unresolved_exterior_visible:
      controlChecks.unresolved_exterior_visible,
    projection_remains_derived:
      controlChecks.projection_status_derived,
    atlas_semantics_preserved:
      controlChecks.atlas_projection_semantics_preserved,
  },
  candidate_relations: {
    atlas_relational_slice_can_preserve_declared_relational_coordinates: 'YES',
    local_relation_coordinate_ne_undifferentiated_relation_bag: 'YES',
    represented_qualified_gap_must_remain_explicit_for_this_slice: 'YES',
    unresolved_exterior_must_remain_visible_for_this_slice: 'YES',
    atlas_projection_identity_ne_operative_world_identity: 'YES',
  },
  effects: {
    relation_discovery_effect: 'NONE',
    renderer_integration_effect: 'NONE',
    work_admission_effect: 'NONE',
    planning_activation_effect: 'NONE',
    authority_effect: 'NONE',
    execution_effect: 'NONE',
    scientific_standing_effect: 'NONE',
  },
  claim_ceiling:
    'One read-only Atlas-shaped relational/topology slice over the exact frozen '
    + 'RIL1/RTL1 synthetic basis plus five controlled ablations. The control '
    + 'tests preservation of local relation, surrounding topology, represented-'
    + 'versus-qualified gap, unresolved exterior, Atlas projection semantics, '
    + 'and neutral effects. The ablations test loss of those coordinates only. '
    + 'No renderer integration, operative-world completeness, automatic relation '
    + 'discovery, universal topology law, trajectory/history law, planning '
    + 'activation, work admission, authority, execution, or scientific standing '
    + 'is created.',
  stopped: 'YES',
};

fs.mkdirSync(path.dirname(OUT), {recursive: true});
fs.writeFileSync(OUT, JSON.stringify(observation, null, 2) + '\n');

console.log(`[OK] wrote ${path.relative(ROOT, OUT)}`);
console.log(`[OK] S0_CONTROL -> ${control.classification}`);
for (const variant of variants) {
  console.log(`[OK] ${variant.variant_id} -> ${variant.classification}`);
}
console.log(`[OK] all_expectations_match ${observation.all_expectations_match}`);
