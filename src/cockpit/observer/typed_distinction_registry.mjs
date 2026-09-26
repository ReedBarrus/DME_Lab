export const TYPED_DISTINCTION_REGISTRY_PATH = '../../../generated/typed_distinction_registry_v0.json';

const OBJECT_TYPE = 'TYPED_DISTINCTION_REGISTRY_PROJECTION_V0';
const CELL_ID = 'DISTINCTION_PATH_IDENTITY_NE_CONTENT_IDENTITY_001';

function required(object, key, scope) {
  if (!object || typeof object !== 'object' || !(key in object)) {
    throw new TypeError(`typed distinction registry missing ${scope}.${key}`);
  }
  return object[key];
}

export function buildTypedDistinctionRegistryModel(source, temporalLineage = null) {
  if (!source || source.object_type !== OBJECT_TYPE) {
    throw new TypeError('unsupported typed distinction registry projection');
  }
  if (source.authority_effect !== 'NONE'
      || source.execution_effect !== 'NONE'
      || source.control_effect !== 'NONE') {
    throw new TypeError('typed distinction registry projection has forbidden effects');
  }
  if (temporalLineage && source.temporal_source_commit !== temporalLineage.source.source_commit) {
    throw new TypeError('typed distinction registry projection is stale for temporal source');
  }
  const sourceRegistry = required(source, 'source_registry', 'source');
  required(sourceRegistry, 'path', 'source_registry');
  required(sourceRegistry, 'sha256', 'source_registry');
  const records = required(source, 'records', 'source');
  if (!Array.isArray(records)) throw new TypeError('typed distinction records must be an array');
  const admitted = [];
  const byId = Object.create(null);
  for (const record of records) {
    if (record.standing !== 'ADMITTED_BOUNDED') continue;
    if (record.distinction_id !== CELL_ID
        || record.object_type !== 'TYPED_DISTINCTION_RECORD_V0'
        || record.relation_type !== 'NOT_EQUAL'
        || record.value?.left !== 'PATH_IDENTITY'
        || record.value?.right !== 'CONTENT_IDENTITY'
        || record.currentness !== 'HISTORICAL_SPECIMEN'
        || record.authority_effect !== 'NONE'
        || record.execution_effect !== 'NONE'
        || record.control_effect !== 'NONE'
        || !record.claim_ceiling
        || !Array.isArray(record.subject_addresses)
        || record.subject_addresses.length !== 1
        || !Array.isArray(record.resolved_source_handles)
        || !record.resolved_source_handles.length
        || !Array.isArray(record.dependencies)
        || !Array.isArray(record.unresolved)) {
      throw new TypeError('admitted typed distinction record violates Cell 001 projection contract');
    }
    if (byId[record.distinction_id]) throw new TypeError('duplicate admitted distinction');
    admitted.push(record);
    byId[record.distinction_id] = record;
  }
  const reconstructionPackets = Array.isArray(source.reconstruction_packets)
    ? source.reconstruction_packets : [];
  const packetByDistinctionId = Object.fromEntries(reconstructionPackets.map((packet) => (
    [packet.distinction_address, packet]
  )));
  return {source, admitted, byId, packetByDistinctionId};
}

export function distinctionsForObject(registry, object) {
  if (!registry || !object) return [];
  return registry.admitted.filter((record) => {
    const subject = record.subject_addresses[0];
    return subject.substrate === 'repo_path'
      && subject.repository === object.repository_identity
      && subject.path === object.path
      && subject.object_kind === object.object_kind;
  });
}

export function reconstructionHandleFor(registry, distinctionId) {
  if (!registry?.byId?.[distinctionId]) return null;
  const packet = registry.packetByDistinctionId[distinctionId];
  if (!packet) return null;
  return {
    distinction_address: distinctionId,
    registry_path: registry.source.source_registry.path,
    registry_sha256: registry.source.source_registry.sha256,
    packet,
  };
}
