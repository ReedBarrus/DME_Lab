export const STRUCTURAL_BASIS_V0 = Object.freeze({
  containment: 1.0,
  dependency: 0.35,
  version: 0.10,
});

export const DYNAMIC_BASIS_V0 = Object.freeze({
  authority: 0.50,
  consequence: 0.50,
});

const DEPENDENCY_RELATIONS = new Set([
  'DEPENDS_ON', 'IMPORTS', 'REFERENCES', 'SEAT_HAS_CURSOR', 'CURSOR_REFERENCES_STATE',
]);
const STRUCTURAL_RELATIONS = new Set(['CONTAINS', 'HAS_VERSION', 'PROJECTS_ACTOR']);
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

const zero = () => ({x: 0, y: 0, z: 0});
const add = (left, right) => ({
  x: left.x + right.x,
  y: left.y + right.y,
  z: left.z + right.z,
});
const subtract = (left, right) => ({
  x: left.x - right.x,
  y: left.y - right.y,
  z: left.z - right.z,
});
const scale = (point, amount) => ({
  x: point.x * amount,
  y: point.y * amount,
  z: point.z * amount,
});
const length = (point) => Math.hypot(point.x, point.y, point.z);

function hash32(value) {
  let hash = 0x811c9dc5;
  for (const character of String(value)) {
    hash ^= character.codePointAt(0);
    hash = Math.imul(hash, 0x01000193);
  }
  return hash >>> 0;
}

function deterministicUnit(seed, rank = 0, total = 1) {
  const phase = (hash32(seed) / 0x100000000) * Math.PI * 2;
  const y = 1 - (2 * (rank + 0.5)) / Math.max(1, total);
  const radial = Math.sqrt(Math.max(0, 1 - y * y));
  const angle = phase + rank * GOLDEN_ANGLE;
  return {x: Math.cos(angle) * radial, y, z: Math.sin(angle) * radial};
}

function orderedChildren(children, objectById) {
  return [...children].sort((left, right) => {
    const leftObject = objectById[left];
    const rightObject = objectById[right];
    const leftRank = hash32(`${leftObject.object_kind}:${left}`);
    const rightRank = hash32(`${rightObject.object_kind}:${right}`);
    return leftRank - rightRank || left.localeCompare(right);
  });
}

function localRadius(parent, child, depth, siblingCount) {
  if (child.object_kind === 'file_version') return 0;
  if (child.object_kind === 'seat') return 520;
  if (child.object_kind === 'cursor') return 430;
  const density = Math.max(1, Math.cbrt(siblingCount));
  if (parent.object_kind === 'repository') {
    return child.object_kind === 'directory'
      ? 360 + density * 34
      : 260 + density * 22;
  }
  if (child.object_kind === 'directory') {
    return Math.max(72, 210 / Math.pow(Math.max(1, depth), 0.46)) + density * 12;
  }
  return Math.max(22, 72 / Math.pow(Math.max(1, depth), 0.32)) + density * 9;
}

function weightedPosition(components, structural, dynamic) {
  return add(
    add(
      scale(components.containment, structural.containment),
      scale(components.dependency, structural.dependency),
    ),
    add(
      scale(components.version, structural.version),
      add(
        scale(components.authority, dynamic.authority),
        scale(components.consequence, dynamic.consequence),
      ),
    ),
  );
}

function finiteWeight(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

export function buildGeometricRepositoryField(model) {
  const repository = model.objects.find((object) => object.object_kind === 'repository');
  if (!repository) throw new TypeError('geometric field requires one repository anchor');

  const parentById = Object.create(null);
  const childrenById = Object.create(null);
  const structuralEdges = [];
  const dependencyEdges = [];

  for (const relation of model.source.relations) {
    if (!relation.target_id || !model.objectById[relation.target_id]) continue;
    if (STRUCTURAL_RELATIONS.has(relation.relation)) {
      if (parentById[relation.target_id]) {
        throw new TypeError(`multiple structural parents for ${relation.target_id}`);
      }
      parentById[relation.target_id] = relation.source_id;
      if (!childrenById[relation.source_id]) childrenById[relation.source_id] = [];
      childrenById[relation.source_id].push(relation.target_id);
      structuralEdges.push(relation);
    } else if (DEPENDENCY_RELATIONS.has(relation.relation)) {
      dependencyEdges.push(relation);
    }
  }

  const containmentById = Object.create(null);
  const depthById = Object.create(null);
  const active = new Set();

  function place(objectId, parentPosition = zero(), depth = 0) {
    if (active.has(objectId)) throw new TypeError('structural relation cycle in repository fabric');
    active.add(objectId);
    const object = model.objectById[objectId];
    const childIds = orderedChildren(childrenById[objectId] || [], model.objectById);
    containmentById[objectId] = parentPosition;
    depthById[objectId] = depth;
    for (let index = 0; index < childIds.length; index += 1) {
      const childId = childIds[index];
      const child = model.objectById[childId];
      const layoutIdentity = model.source.layout_identity || model.source.source_commit;
      const unit = deterministicUnit(`${layoutIdentity}:${objectId}`, index, childIds.length);
      const radius = localRadius(object, child, depth + 1, childIds.length);
      const jitter = 0.82 + (hash32(childId) % 3700) / 10000;
      place(childId, add(parentPosition, scale(unit, radius * jitter)), depth + 1);
    }
    active.delete(objectId);
  }

  place(repository.object_id);
  for (const object of model.objects) {
    if (!containmentById[object.object_id]) {
      throw new TypeError(`repository object lacks structural closure: ${object.object_id}`);
    }
  }

  const dependencyById = Object.fromEntries(model.objects.map((object) => [object.object_id, zero()]));
  for (const relation of dependencyEdges) {
    const source = containmentById[relation.source_id];
    const target = containmentById[relation.target_id];
    const pull = scale(subtract(target, source), 0.18);
    dependencyById[relation.source_id] = add(dependencyById[relation.source_id], pull);
    dependencyById[relation.target_id] = add(dependencyById[relation.target_id], scale(pull, -1));
  }

  const versionById = Object.create(null);
  for (const object of model.objects) {
    if (object.object_kind !== 'file_version') {
      versionById[object.object_id] = zero();
      continue;
    }
    const direction = deterministicUnit(`${object.object_id}:version`, 0, 1);
    versionById[object.object_id] = scale(direction, 180);
  }

  const weights = {
    structural: {...STRUCTURAL_BASIS_V0},
    dynamic: {...DYNAMIC_BASIS_V0},
  };
  const nodes = model.objects.map((object) => {
    const components = {
      containment: containmentById[object.object_id],
      dependency: dependencyById[object.object_id],
      version: versionById[object.object_id],
      authority: zero(),
      consequence: zero(),
    };
    const restPosition = weightedPosition(
      components,
      STRUCTURAL_BASIS_V0,
      DYNAMIC_BASIS_V0,
    );
    return {
      objectId: object.object_id,
      objectKind: object.object_kind,
      sourceObject: object,
      depth: depthById[object.object_id],
      components,
      restPosition,
      currentPosition: {...restPosition},
    };
  });
  const nodeById = Object.fromEntries(nodes.map((node) => [node.objectId, node]));
  const volumeRadiusById = Object.create(null);
  for (const node of nodes) {
    const children = childrenById[node.objectId] || [];
    volumeRadiusById[node.objectId] = Math.max(
      node.objectKind === 'repository' ? 80 : 14,
      ...children.map((childId) => length(subtract(
        nodeById[childId].restPosition,
        node.restPosition,
      )) + 12),
    );
  }

  const field = {
    layoutAlgorithm: 'DETERMINISTIC_HIERARCHICAL_RADIAL_VOLUME_V0',
    sourceCommit: model.source.source_commit,
    nodes,
    nodeById,
    structuralEdges,
    dependencyEdges,
    childrenById,
    parentById,
    volumeRadiusById,
    weights,
    dynamicStanding: {
      authority: 'UNAVAILABLE',
      consequence: 'UNAVAILABLE',
    },
    camera: {
      yaw: -0.62,
      pitch: 0.42,
      distance: 1200,
      target: zero(),
    },
  };
  resetWholeFieldCamera(field);
  return field;
}

export function setGeometricBasisWeights(field, next) {
  const structural = next.structural || {};
  const dynamic = next.dynamic || {};
  field.weights.structural = {
    containment: finiteWeight(structural.containment, field.weights.structural.containment),
    dependency: finiteWeight(structural.dependency, field.weights.structural.dependency),
    version: finiteWeight(structural.version, field.weights.structural.version),
  };
  field.weights.dynamic = {
    authority: finiteWeight(dynamic.authority, field.weights.dynamic.authority),
    consequence: finiteWeight(dynamic.consequence, field.weights.dynamic.consequence),
  };
  for (const node of field.nodes) {
    node.currentPosition = weightedPosition(
      node.components,
      field.weights.structural,
      field.weights.dynamic,
    );
  }
  return field;
}

function fieldBounds(field) {
  if (!field.nodes.length) return {center: zero(), radius: 1};
  const minimum = {x: Infinity, y: Infinity, z: Infinity};
  const maximum = {x: -Infinity, y: -Infinity, z: -Infinity};
  for (const node of field.nodes) {
    const point = node.currentPosition;
    minimum.x = Math.min(minimum.x, point.x);
    minimum.y = Math.min(minimum.y, point.y);
    minimum.z = Math.min(minimum.z, point.z);
    maximum.x = Math.max(maximum.x, point.x);
    maximum.y = Math.max(maximum.y, point.y);
    maximum.z = Math.max(maximum.z, point.z);
  }
  const center = scale(add(minimum, maximum), 0.5);
  let radius = 1;
  for (const node of field.nodes) {
    radius = Math.max(radius, length(subtract(node.currentPosition, center)));
  }
  return {center, radius};
}

export function resetWholeFieldCamera(field) {
  const bounds = fieldBounds(field);
  field.camera.target = bounds.center;
  field.camera.distance = Math.max(180, bounds.radius * 2.55);
  field.camera.yaw = -0.62;
  field.camera.pitch = 0.42;
  return field;
}

export function focusFieldObject(field, objectId) {
  const node = field.nodeById[objectId];
  if (!node) return field;
  field.camera.target = {...node.currentPosition};
  field.camera.distance = Math.max(70, (field.volumeRadiusById[objectId] || 18) * 3.4);
  return field;
}

export function orbitFieldCamera(field, deltaYaw, deltaPitch) {
  field.camera.yaw += deltaYaw;
  field.camera.pitch = Math.max(-1.45, Math.min(1.45, field.camera.pitch + deltaPitch));
  return field;
}

export function panFieldCamera(field, deltaX, deltaY) {
  const amount = field.camera.distance / 650;
  const right = {x: Math.cos(field.camera.yaw), y: 0, z: -Math.sin(field.camera.yaw)};
  const up = {
    x: Math.sin(field.camera.yaw) * Math.sin(field.camera.pitch),
    y: Math.cos(field.camera.pitch),
    z: Math.cos(field.camera.yaw) * Math.sin(field.camera.pitch),
  };
  field.camera.target = add(
    field.camera.target,
    add(scale(right, -deltaX * amount), scale(up, deltaY * amount)),
  );
  return field;
}

export function dollyFieldCamera(field, delta) {
  field.camera.distance = Math.max(24, Math.min(20000, field.camera.distance * Math.exp(delta)));
  return field;
}

export function projectFieldPoint(point, camera, width, height) {
  const relative = subtract(point, camera.target);
  const cosYaw = Math.cos(camera.yaw);
  const sinYaw = Math.sin(camera.yaw);
  const x1 = cosYaw * relative.x - sinYaw * relative.z;
  const z1 = sinYaw * relative.x + cosYaw * relative.z;
  const cosPitch = Math.cos(camera.pitch);
  const sinPitch = Math.sin(camera.pitch);
  const y2 = cosPitch * relative.y - sinPitch * z1;
  const z2 = sinPitch * relative.y + cosPitch * z1;
  const depth = camera.distance - z2;
  if (depth <= 1) return {visible: false, x: 0, y: 0, depth, scale: 0};
  const focal = Math.min(width, height) * 0.86;
  const perspective = focal / depth;
  return {
    visible: true,
    x: width / 2 + x1 * perspective,
    y: height / 2 - y2 * perspective,
    depth,
    scale: perspective,
  };
}

export function repositoryFieldRelationCounts(field) {
  const counts = {
    containment: field.structuralEdges.filter((edge) => edge.relation === 'CONTAINS').length,
    version: field.structuralEdges.filter((edge) => edge.relation === 'HAS_VERSION').length,
    dependency: field.dependencyEdges.filter((edge) => DEPENDENCY_RELATIONS.has(edge.relation)
      && !['SEAT_HAS_CURSOR', 'CURSOR_REFERENCES_STATE'].includes(edge.relation)).length,
  };
  const actor = field.dependencyEdges.filter((edge) => ['SEAT_HAS_CURSOR', 'CURSOR_REFERENCES_STATE'].includes(edge.relation)).length;
  if (actor) counts.actor = actor;
  return counts;
}
