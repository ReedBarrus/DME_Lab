export const REPOSITORY_FABRIC_PATH = '../../../generated/repository_address_fabric.json';

const ALLOWED_KINDS = new Set(['repository', 'directory', 'file', 'file_version', 'seat', 'cursor']);

function required(object, key, scope) {
  if (object === null || typeof object !== 'object' || !(key in object)) {
    throw new TypeError(`repository fabric missing ${scope}.${key}`);
  }
  return object[key];
}

export function buildRepositoryFabricModel(source) {
  if (!source || source.object_type !== 'REPOSITORY_ADDRESS_FABRIC_V0') {
    throw new TypeError('unsupported repository address fabric source');
  }
  const objects = required(source, 'objects', 'source');
  const relations = required(source, 'relations', 'source');
  if (!Array.isArray(objects) || !Array.isArray(relations)) {
    throw new TypeError('repository fabric objects and relations must be arrays');
  }

  const objectById = Object.create(null);
  for (const object of objects) {
    const id = required(object, 'object_id', 'object');
    const kind = required(object, 'object_kind', id);
    if (!ALLOWED_KINDS.has(kind)) {
      throw new TypeError(`unsupported repository fabric object kind ${kind}`);
    }
    if (objectById[id]) throw new TypeError(`duplicate repository fabric object ${id}`);
    objectById[id] = object;
  }

  const outgoingById = Object.create(null);
  const incomingById = Object.create(null);
  for (const relation of relations) {
    const sourceId = relation.source_id;
    if (!outgoingById[sourceId]) outgoingById[sourceId] = [];
    outgoingById[sourceId].push(relation);
    if (relation.target_id) {
      if (!incomingById[relation.target_id]) incomingById[relation.target_id] = [];
      incomingById[relation.target_id].push(relation);
    }
  }

  const repositoryObject = objects.find((object) => object.object_kind === 'repository');
  if (!repositoryObject) throw new TypeError('repository fabric has no repository object');

  return {
    source,
    objects,
    objectById,
    outgoingById,
    incomingById,
    selectedObjectId: repositoryObject.object_id,
    query: '',
  };
}

export function selectRepositoryObject(model, objectId) {
  if (!model.objectById[objectId]) return model;
  return {...model, selectedObjectId: objectId};
}

export function setRepositoryQuery(model, query) {
  return {...model, query: String(query ?? '')};
}

export function selectedRepositoryObject(model) {
  return model.objectById[model.selectedObjectId] || null;
}

export function visibleRepositoryObjects(model) {
  const query = model.query.trim().toLowerCase();
  if (!query) return model.objects;
  return model.objects.filter((object) => [
    object.object_id,
    object.object_kind,
    object.path || '/',
    object.semantic_standing,
    object.git_blob_identity,
    object.content_identity,
    JSON.stringify(object.address),
  ].some((value) => String(value ?? '').toLowerCase().includes(query)));
}

export const repositoryQueryMatches = visibleRepositoryObjects;

export function exactRepositoryQueryMatch(model) {
  const query = model.query.trim();
  if (!query) return null;
  return model.objects.find((object) => (
    object.object_id === query
    || (object.path || '/') === query
    || JSON.stringify(object.address) === query
  )) || visibleRepositoryObjects(model)[0] || null;
}

export function repositoryObjectRelations(model, objectId) {
  return {
    incoming: model.incomingById[objectId] || [],
    outgoing: model.outgoingById[objectId] || [],
  };
}
