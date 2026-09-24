export const DEFAULT_COCKPIT_SURFACE = 'ATLAS';
export const COCKPIT_SURFACES = Object.freeze(['ATLAS', 'LEGACY_OBSERVER']);

export function selectCockpitSurface(state, surface) {
  return COCKPIT_SURFACES.includes(surface) ? {...state, surface} : state;
}

export function atlasFrameUrlWithRuntime(pageHref, frameSrc) {
  const page = new URL(pageHref);
  const frame = new URL(frameSrc, page);
  for (const key of ['runtime', 'control']) {
    const value = page.searchParams.get(key);
    if (value) frame.searchParams.set(key, value);
  }
  return frame.toString();
}

function startAtlasLanding() {
  const atlas = document.querySelector('#atlas-primary-root');
  const legacy = document.querySelector('#legacy-observer-shell');
  const atlasFrame = document.querySelector('#atlas-primary-frame');
  if (!atlas || !legacy) return null;
  if (atlasFrame) {
    atlasFrame.src = atlasFrameUrlWithRuntime(window.location.href, atlasFrame.getAttribute('src'));
  }
  let state = {surface: DEFAULT_COCKPIT_SURFACE};

  function render() {
    atlas.hidden = state.surface !== 'ATLAS';
    legacy.hidden = state.surface !== 'LEGACY_OBSERVER';
    document.body.classList.toggle('is-legacy-observer', state.surface === 'LEGACY_OBSERVER');
    document.querySelectorAll('[data-cockpit-surface]').forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.cockpitSurface === state.surface));
    });
  }

  document.addEventListener('click', (event) => {
    const button = event.target.closest('[data-cockpit-surface]');
    if (!button) return;
    state = selectCockpitSurface(state, button.dataset.cockpitSurface);
    render();
  });
  render();
  return {getState: () => ({...state})};
}

if (typeof document !== 'undefined') startAtlasLanding();
