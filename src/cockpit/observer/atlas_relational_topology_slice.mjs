export const ATLAS_RELATIONAL_TOPOLOGY_SLICE_OBJECT_TYPE =
  'ATLAS_RELATIONAL_TOPOLOGY_SLICE_V0';

export const REQUIRED_ATLAS_RELATIONAL_SEMANTICS = Object.freeze([
  'RELATION_DRIVEN_FIELD',
  'UNRESOLVED_REMAINS_VISIBLE',
  'PROJECTION_NE_OPERATIVE_WORLD',
  'NO_AUTHORITY_FROM_PROJECTION',
]);

const UNRESOLVED = 'UNRESOLVED_FROM_SLICE';

function clone(value) {
  return value === undefined ? undefined : structuredClone(value);
}

function relationKey(relation) {
  if (!relation || typeof relation !== 'object') return null;
  return [
    relation.relation_id,
    relation.source,
    relation.target,
    relation.load,
  ].join('|');
}

function edgeMap(topology) {
  const edges = Array.isArray(topology?.relations) ? topology.relations : [];
  return new Map(edges.map((edge) => [edge.relation_id, edge]));
}

function semanticsMatch(source) {
  const actual = Array.isArray(source?.atlas_projection_semantics)
    ? [...source.atlas_projection_semantics].sort()
    : [];
  const expected = [...REQUIRED_ATLAS_RELATIONAL_SEMANTICS].sort();
  return JSON.stringify(actual) === JSON.stringify(expected);
}

export function reconstructAtlasRelationalTopologySlice(source) {
  const localRelation = source?.local_relation
    ? clone(source.local_relation)
    : UNRESOLVED;

  const surroundingTopology = source?.surrounding_topology
    ? clone(source.surrounding_topology)
    : UNRESOLVED;

  const representedTopology = source?.represented_topology
    ? clone(source.represented_topology)
    : UNRESOLVED;

  const qualifiedTopology = source?.qualified_specimen_topology
    ? clone(source.qualified_specimen_topology)
    : UNRESOLVED;

  const declaredGap = source?.represented_vs_qualified_gap
    ? clone(source.represented_vs_qualified_gap)
    : UNRESOLVED;

  const unresolvedExterior = source?.unresolved_exterior
    ? clone(source.unresolved_exterior)
    : UNRESOLVED;

  const representedEdges = edgeMap(source?.represented_topology);
  const qualifiedEdges = edgeMap(source?.qualified_specimen_topology);

  let derivedGap = UNRESOLVED;
  if (representedEdges.size || qualifiedEdges.size) {
    const omitted = [];
    for (const [id, edge] of qualifiedEdges.entries()) {
      const represented = representedEdges.get(id);
      if (!represented || relationKey(represented) !== relationKey(edge)) {
        omitted.push(clone(edge));
      }
    }
    derivedGap = {
      omitted_or_changed_relations: omitted,
      relation_ids: omitted.map((edge) => edge.relation_id),
    };
  }

  const localRelationId = source?.local_relation?.relation_id;
  const localInRepresented = localRelationId
    ? representedEdges.has(localRelationId)
    : false;
  const localInQualified = localRelationId
    ? qualifiedEdges.has(localRelationId)
    : false;

  const surroundingIds = Array.isArray(source?.surrounding_topology?.relation_ids)
    ? source.surrounding_topology.relation_ids
    : [];
  const surroundingRecovered = surroundingIds.length
    ? surroundingIds.every((id) => qualifiedEdges.has(id))
    : false;

  const projectionSemantics = semanticsMatch(source)
    ? clone(source.atlas_projection_semantics)
    : UNRESOLVED;

  const checks = {
    source_object_type_supported:
      source?.object_type === ATLAS_RELATIONAL_TOPOLOGY_SLICE_OBJECT_TYPE,
    projection_status_derived:
      source?.projection_status === 'DERIVED_PROJECTION_NOT_WORLD_TRUTH',
    effects_neutral:
      source?.authority_effect === 'NONE'
      && source?.execution_effect === 'NONE'
      && source?.control_effect === 'NONE',
    atlas_projection_semantics_preserved: projectionSemantics !== UNRESOLVED,
    local_relation_recoverable:
      localRelation !== UNRESOLVED && localInRepresented && localInQualified,
    surrounding_topology_recoverable:
      surroundingTopology !== UNRESOLVED && surroundingRecovered,
    represented_topology_recoverable:
      representedTopology !== UNRESOLVED,
    qualified_specimen_topology_recoverable:
      qualifiedTopology !== UNRESOLVED,
    represented_vs_qualified_gap_recoverable:
      declaredGap !== UNRESOLVED
      && derivedGap !== UNRESOLVED
      && Array.isArray(declaredGap.relation_ids)
      && JSON.stringify([...declaredGap.relation_ids].sort())
        === JSON.stringify([...derivedGap.relation_ids].sort()),
    unresolved_exterior_visible:
      unresolvedExterior !== UNRESOLVED
      && unresolvedExterior.status === 'OPEN',
  };

  return {
    object_type: 'ATLAS_RELATIONAL_TOPOLOGY_SLICE_RECONSTRUCTION_V0',
    slice_id: source?.slice_id || UNRESOLVED,
    projection_status: source?.projection_status || UNRESOLVED,
    atlas_projection_semantics: projectionSemantics,
    local_relation: localRelation,
    surrounding_topology: surroundingTopology,
    represented_topology: representedTopology,
    qualified_specimen_topology: qualifiedTopology,
    represented_vs_qualified_gap: declaredGap,
    derived_gap: derivedGap,
    unresolved_exterior: unresolvedExterior,
    basis_handles: Array.isArray(source?.basis_handles)
      ? clone(source.basis_handles)
      : UNRESOLVED,
    checks,
    all_checks_pass: Object.values(checks).every(Boolean),
    authority_effect: 'NONE',
    execution_effect: 'NONE',
    control_effect: 'NONE',
  };
}

export function classifyAtlasRelationalTopologySlice(source) {
  const reconstructed = reconstructAtlasRelationalTopologySlice(source);
  if (reconstructed.all_checks_pass) return 'BOUNDED_SLICE_READY';

  const checks = reconstructed.checks;
  if (!checks.local_relation_recoverable) return 'HOLD_LOCAL_RELATION_LOST';
  if (!checks.surrounding_topology_recoverable) return 'HOLD_SURROUNDING_TOPOLOGY_LOST';
  if (!checks.represented_vs_qualified_gap_recoverable) return 'HOLD_TOPOLOGY_GAP_LOST';
  if (!checks.unresolved_exterior_visible) return 'HOLD_UNRESOLVED_EXTERIOR_LOST';
  if (!checks.atlas_projection_semantics_preserved) return 'HOLD_ATLAS_SEMANTICS_LOST';
  return 'HOLD_SLICE_CONTRACT_INCOMPLETE';
}
