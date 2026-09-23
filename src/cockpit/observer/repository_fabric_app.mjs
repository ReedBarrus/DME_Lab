import {
  REPOSITORY_FABRIC_PATH,
  buildRepositoryFabricModel,
  selectRepositoryObject,
  setRepositoryQuery,
} from './repository_fabric_model.mjs';
import {
  renderRepositoryFabric,
  renderRepositoryFabricUnavailable,
} from './repository_fabric_render.mjs';

const root = document.querySelector('#repository-fabric-root');
let model = null;

function render() {
  root.innerHTML = renderRepositoryFabric(model);
}

root.addEventListener('click', async (event) => {
  const objectButton = event.target.closest('[data-repository-object-id]');
  if (objectButton) {
    model = selectRepositoryObject(model, objectButton.dataset.repositoryObjectId);
    render();
    return;
  }
  const copyButton = event.target.closest('[data-copy-repository-address]');
  if (copyButton) {
    const object = model.objectById[copyButton.dataset.copyRepositoryAddress];
    if (!object) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(object.address));
      copyButton.textContent = 'ADDRESS COPIED';
    } catch {
      copyButton.textContent = 'COPY UNAVAILABLE';
    }
  }
});

root.addEventListener('input', (event) => {
  if (!event.target.matches('[data-repository-query]')) return;
  const cursor = event.target.selectionStart;
  model = setRepositoryQuery(model, event.target.value);
  render();
  const input = root.querySelector('[data-repository-query]');
  input?.focus({preventScroll: true});
  if (cursor !== null) input?.setSelectionRange(cursor, cursor);
});

async function load() {
  try {
    const response = await fetch(REPOSITORY_FABRIC_PATH, {
      method: 'GET',
      cache: 'no-store',
      credentials: 'same-origin',
    });
    if (!response.ok) throw new Error(`source fetch failed with HTTP ${response.status}`);
    model = buildRepositoryFabricModel(await response.json());
    render();
  } catch (error) {
    root.innerHTML = renderRepositoryFabricUnavailable(
      error instanceof Error ? error.message : String(error),
    );
  }
}

load();
