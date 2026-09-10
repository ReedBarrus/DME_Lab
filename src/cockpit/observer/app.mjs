import {
  buildObserverModel,
  followEvidence,
  followPressureRelation,
  loadProjection,
  openLineage,
  selectConstraint,
  selectEvidence,
  selectOccurrence,
  selectProjectionDocument,
  selectView,
} from './model.mjs';
import {
  renderActiveView,
  renderDiagnostics,
  renderHeader,
  renderNavigation,
  renderViewNavigation,
  unavailableMarkup,
} from './render.mjs';

const roots = {
  header: document.querySelector('#repository-root'),
  navigation: document.querySelector('#navigation-root'),
  viewNavigation: document.querySelector('#view-navigation-root'),
  view: document.querySelector('#view-root'),
  diagnostics: document.querySelector('#diagnostics-root'),
  failure: document.querySelector('#failure-root'),
};

let viewModel = null;

function projectionUrl() {
  const requested = new URL(window.location.href).searchParams.get('model');
  return requested || '../../../generated/cockpit_projection.json';
}

function render() {
  if (!viewModel) {
    return;
  }
  roots.header.innerHTML = renderHeader(viewModel);
  roots.navigation.innerHTML = renderNavigation(viewModel);
  roots.viewNavigation.innerHTML = renderViewNavigation(viewModel);
  roots.view.innerHTML = renderActiveView(viewModel);
  roots.diagnostics.innerHTML = renderDiagnostics(viewModel);
  roots.failure.replaceChildren();

  document.querySelectorAll('[data-view]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = selectView(viewModel, button.dataset.view);
      render();
    });
  });

  document.querySelectorAll('[data-occurrence-key]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = selectOccurrence(viewModel, button.dataset.occurrenceKey);
      render();
    });
  });

  document.querySelectorAll('[data-open-lineage-key]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = openLineage(viewModel, button.dataset.openLineageKey);
      render();
    });
  });

  document.querySelectorAll('[data-follow-relation-key]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = followPressureRelation(
        viewModel,
        button.dataset.followRelationKey,
        button.dataset.fromOccurrenceKey,
      );
      render();
    });
  });

  document.querySelectorAll('[data-constraint-key]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = selectConstraint(viewModel, button.dataset.constraintKey);
      render();
    });
  });

  document.querySelectorAll('[data-evidence-key]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = selectEvidence(viewModel, button.dataset.evidenceKey);
      render();
    });
  });

  document.querySelectorAll('[data-follow-evidence-key]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = followEvidence(
        viewModel,
        button.dataset.evidenceOwnerKind,
        button.dataset.evidenceOwnerKey,
        button.dataset.followEvidenceKey,
      );
      render();
    });
  });

  document.querySelectorAll('[data-projection-document-key]').forEach((button) => {
    button.addEventListener('click', () => {
      viewModel = selectProjectionDocument(
        viewModel,
        button.dataset.projectionDocumentKey,
      );
      render();
    });
  });

  document.querySelectorAll('[data-filter-target]').forEach((input) => {
    input.addEventListener('input', () => {
      const query = input.value.trim().toLowerCase();
      const target = input.dataset.filterTarget;
      if (target !== 'constraint-card' && target !== 'source-card') {
        return;
      }
      document.querySelectorAll('.' + target).forEach((item) => {
        item.hidden = query.length > 0 && !item.dataset.filterText.includes(query);
      });
    });
  });

  document.querySelectorAll('[data-copy-value]').forEach((copyButton) => {
    copyButton.addEventListener('click', async () => {
      const value = copyButton.dataset.copyValue || '';
      try {
        await navigator.clipboard.writeText(value);
        copyButton.textContent = 'Copied';
      } catch {
        copyButton.textContent = 'Copy unavailable';
      }
    });
  });
}

function renderFailure(error) {
  viewModel = null;
  roots.header.replaceChildren();
  roots.navigation.replaceChildren();
  roots.viewNavigation.replaceChildren();
  roots.view.replaceChildren();
  roots.diagnostics.replaceChildren();
  roots.failure.innerHTML = unavailableMarkup(error instanceof Error ? error.message : String(error));
  document.body.dataset.projectionState = 'unavailable';
}

async function start() {
  document.body.dataset.projectionState = 'loading';
  try {
    viewModel = await loadProjection(window.fetch.bind(window), projectionUrl());
    document.body.dataset.projectionState =
      viewModel.repositoryState?.projection_status || 'missing';
    render();
  } catch (error) {
    renderFailure(error);
  }
}

start();
