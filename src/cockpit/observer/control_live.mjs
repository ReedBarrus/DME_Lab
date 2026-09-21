const VERBS = ['FOCUS', 'ASSIGN', 'RELEASE', 'RING'];
const PREP_KINDS = [
  'RESOLVE_REFS',
  'REVALIDATE_BASIS',
  'ASSEMBLE_EVIDENCE',
  'DRAFT_PACKET',
  'REQUEST_REVIEW',
  'REVIEW_RESULT',
  'ESTIMATE_RESOURCES',
  'DETECT_CONFLICTS',
  'DERIVE_STOP_CONDITIONS',
];

function node(tag, value = '', className = '') {
  const item = document.createElement(tag);
  if (value !== '') item.textContent = value;
  if (className) item.className = className;
  return item;
}

function field(label, input) {
  const wrap = document.createElement('label');
  wrap.className = 'control-field';
  wrap.append(node('span', label, 'control-field-label'), input);
  return wrap;
}

function input(name, placeholder = '') {
  const item = document.createElement('input');
  item.name = name;
  item.placeholder = placeholder;
  item.autocomplete = 'off';
  return item;
}

function select(name, values) {
  const item = document.createElement('select');
  item.name = name;
  for (const value of values) {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    item.append(option);
  }
  return item;
}

function generatedGestureId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }
  return 'gesture-' + Date.now() + '-' + Math.floor(Math.random() * 1e9);
}

export function buildControlIntent(values) {
  const verb = values.verb;
  if (!VERBS.includes(verb)) {
    throw new Error('unsupported Cockpit control verb');
  }
  const common = {
    verb,
    gesture_id: values.gesture_id,
    reason: values.reason || null,
  };
  if (verb === 'FOCUS') {
    return {
      ...common,
      campaign_id: values.campaign_id,
      request_id: values.request_id,
    };
  }
  if (verb === 'ASSIGN') {
    return {
      ...common,
      campaign_id: values.campaign_id,
      request_id: values.request_id,
      seat_id: values.seat_id,
      preparation_kind: values.preparation_kind,
    };
  }
  return {
    ...common,
    campaign_id: values.campaign_id,
    assignment_id: values.assignment_id,
  };
}

export function controlPath(base, suffix) {
  return String(base).replace(/\/$/, '') + suffix;
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  });
  const value = await response.json();
  if (!response.ok) {
    throw new Error(value?.error || 'control request failed: ' + response.status);
  }
  return value;
}

async function getJson(url) {
  const response = await fetch(url);
  const value = await response.json();
  if (!response.ok) {
    throw new Error(value?.error || 'control request failed: ' + response.status);
  }
  return value;
}

function renderUnavailable(root, message) {
  root.replaceChildren();
  root.className = 'control-panel control-unavailable';
  root.append(node('h2', 'CONTROL MEMBRANE'));
  root.append(node('p', message));
  root.append(
    node(
      'p',
      'LIVE PROJECTION ≠ CONTROL PATH · no adapter means no Cockpit writes.',
      'runtime-footnote',
    ),
  );
}

export function startControlAdapter(root) {
  if (!root) return null;
  const params = new URL(window.location.href).searchParams;
  const base = params.get('control');
  if (!base) {
    renderUnavailable(
      root,
      'Control adapter not configured. Add ?control=http://127.0.0.1:8770 to enable typed human gestures.',
    );
    return null;
  }

  root.replaceChildren();
  root.className = 'control-panel';
  root.append(node('h2', 'CONTROL MEMBRANE'));
  root.append(
    node(
      'p',
      'Explicit human gesture → exact object preview → explicit confirmation → qualified store.',
      'control-subtitle',
    ),
  );

  const form = document.createElement('form');
  form.className = 'control-form';

  const verb = select('verb', VERBS);
  const gesture = input('gesture_id');
  gesture.value = generatedGestureId();
  const campaign = input('campaign_id', 'COCKPIT_OPERATING_SPACE_001');
  const request = input('request_id', 'COS-E1');
  const assignment = input('assignment_id', 'CCA-A-…');
  const seat = input('seat_id', 'MAYA');
  const prep = select('preparation_kind', PREP_KINDS);
  const reason = input('reason', 'optional narrative');

  const requestWrap = field('REQUEST', request);
  const assignmentWrap = field('ASSIGNMENT', assignment);
  const seatWrap = field('SEAT', seat);
  const prepWrap = field('PREPARATION KIND', prep);

  form.append(
    field('VERB', verb),
    field('GESTURE ID', gesture),
    field('CAMPAIGN', campaign),
    requestWrap,
    assignmentWrap,
    seatWrap,
    prepWrap,
    field('REASON', reason),
  );

  const actions = document.createElement('div');
  actions.className = 'control-actions';
  const previewButton = node('button', 'PREVIEW EXACT OBJECT', 'control-preview-button');
  previewButton.type = 'submit';
  const confirmButton = node('button', 'CONFIRM + APPEND', 'control-confirm-button');
  confirmButton.type = 'button';
  confirmButton.disabled = true;
  const refreshButton = node('button', 'REFRESH HANDLES', 'control-refresh-button');
  refreshButton.type = 'button';
  actions.append(previewButton, confirmButton, refreshButton);
  form.append(actions);
  root.append(form);

  const handles = node('pre', '', 'control-handles');
  const previewBox = node('pre', 'No object previewed.', 'control-preview');
  const resultBox = node('pre', '', 'control-result');
  root.append(handles, previewBox, resultBox);

  let retainedPreview = null;

  function updateFields() {
    const v = verb.value;
    requestWrap.hidden = !['FOCUS', 'ASSIGN'].includes(v);
    assignmentWrap.hidden = !['RELEASE', 'RING'].includes(v);
    seatWrap.hidden = v !== 'ASSIGN';
    prepWrap.hidden = v !== 'ASSIGN';
    retainedPreview = null;
    confirmButton.disabled = true;
    previewBox.textContent = 'No object previewed.';
    resultBox.textContent = '';
  }

  async function refreshHandles() {
    handles.textContent = 'Loading current control handles…';
    try {
      const state = await getJson(controlPath(base, '/control/state'));
      const selections = state.current_selection || [];
      const assignments = state.assignment_projection || [];
      handles.textContent = [
        'basis: ' + ((state.basis_refs || []).join(', ') || '—'),
        'requests: ' + ((state.requests || []).map((r) => r.request_id).join(', ') || '—'),
        'selected: ' + (selections.map((s) => s.request_id).join(', ') || '—'),
        'assignments: ' + (assignments.map((a) => a.assignment_id + '[' + a.assignment_state + ']').join(', ') || '—'),
      ].join('\n');
    } catch (error) {
      handles.textContent = 'Control state unavailable: ' + error;
    }
  }

  const prefillHandler = (event) => {
    const detail = event?.detail || {};
    if (!VERBS.includes(detail.verb)) return;
    verb.value = detail.verb;
    campaign.value = detail.campaign_id || '';
    request.value = detail.request_id || '';
    assignment.value = detail.assignment_id || '';
    seat.value = detail.seat_id || '';
    updateFields();
    root.scrollIntoView({behavior: 'smooth', block: 'start'});
  };

  window.addEventListener('cockpit-control-prefill', prefillHandler);
  verb.addEventListener('change', updateFields);
  refreshButton.addEventListener('click', refreshHandles);

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    retainedPreview = null;
    confirmButton.disabled = true;
    resultBox.textContent = '';
    if (!gesture.value) gesture.value = generatedGestureId();
    const intent = buildControlIntent({
      verb: verb.value,
      gesture_id: gesture.value,
      campaign_id: campaign.value,
      request_id: request.value,
      assignment_id: assignment.value,
      seat_id: seat.value,
      preparation_kind: prep.value,
      reason: reason.value,
    });
    previewBox.textContent = 'Building exact preview…';
    try {
      retainedPreview = await postJson(
        controlPath(base, '/control/preview'),
        intent,
      );
      previewBox.textContent = JSON.stringify(retainedPreview, null, 2);
      confirmButton.disabled = false;
    } catch (error) {
      previewBox.textContent = 'PREVIEW REJECTED\n' + error;
    }
  });

  confirmButton.addEventListener('click', async () => {
    if (!retainedPreview) return;
    confirmButton.disabled = true;
    resultBox.textContent = 'Appending exact previewed object…';
    try {
      const result = await postJson(
        controlPath(base, '/control/commit'),
        {
          preview: retainedPreview.preview,
          preview_sha256: retainedPreview.preview_sha256,
          confirmed_by: 'REED',
        },
      );
      resultBox.textContent = JSON.stringify(result, null, 2);
      retainedPreview = null;
      gesture.value = generatedGestureId();
      await refreshHandles();
    } catch (error) {
      resultBox.textContent = 'COMMIT REJECTED\n' + error;
    }
  });

  updateFields();
  refreshHandles();

  root.append(
    node(
      'p',
      'BUTTON ≠ MAGIC ACTION · PREVIEW ≠ APPEND · COCKPIT CONTROL ≠ CONTROLLER MUTATION',
      'runtime-footnote',
    ),
  );
  return {base};
}
