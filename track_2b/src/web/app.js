'use strict';

const $ = id => document.getElementById(id);
const FIELD_NAMES = {
  active_issue: 'Current repair', resolved_issue: 'Already resolved',
  requested_visit: 'Requested visit · awaiting confirmation', cancelled_visit: 'Cancelled visit',
  property_address: 'Property address', apartment: 'Apartment / unit', contact_name: 'Tenant'
};
const LANGUAGES = {de:'German', fr:'French', it:'Italian', en:'English'};
const state = {cases:[], recorded:{}, mode:'sample', timeout:180, selected:null, text:'', result:null, approved:new Set(), field:null, editing:false, controller:null, generation:0, drafts:null, tab:'brief'};

function node(tag, className, text) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (text !== undefined) el.textContent = text;
  return el;
}

function announce(message = '', error = false) {
  $('notice').textContent = message;
  $('notice').classList.toggle('error', error);
}

function locate(value, quote, operator = false) {
  if (!value) return {value:null, quote:quote || null, start:null, end:null, evidence_status:'missing'};
  if (operator) return {value, quote:null, start:null, end:null, evidence_status:'operator'};
  const start = quote ? state.text.indexOf(quote) : -1;
  const status = start < 0 ? 'unmatched' : state.text.indexOf(quote, start + 1) >= 0 ? 'ambiguous' : 'matched';
  return {value, quote:quote || null, start:status === 'matched' ? start : null, end:status === 'matched' ? start + quote.length : null, evidence_status:status};
}

function acceptResult(result, origin) {
  state.result = {...result, origin, fields:{}};
  for (const key of Object.keys(FIELD_NAMES)) {
    const field = result.fields?.[key] || {};
    state.result.fields[key] = locate(field.value, field.quote);
  }
  state.approved.clear();
  state.field = 'active_issue';
  render();
}

function stopRequest() {
  state.generation++;
  state.controller?.abort();
  state.controller = null;
  document.body.classList.remove('busy');
  $('analyseButton').disabled = false;
}

function chooseCase(id) {
  stopRequest();
  state.selected = state.cases.find(item => item.id === id) || state.cases[0];
  state.text = state.selected.text;
  state.editing = false;
  state.result = null;
  state.approved.clear();
  $('sourceEditor').value = state.text;
  $('casePicker').value = state.selected.id;
  announce();
  if (state.mode === 'sample') {
    const recorded = state.recorded[state.selected.id];
    acceptResult(recorded?.result || state.selected.example, recorded ? 'recorded' : 'example');
  } else render();
}

function renderSource() {
  const language = state.result?.language || state.selected?.language || 'en';
  $('languageBadge').textContent = language.toUpperCase();
  $('languageBadge').title = LANGUAGES[language] || language;
  $('sourceLength').textContent = `${state.text.length.toLocaleString()} characters`;
  $('sourceLabel').textContent = state.text === state.selected?.text ? 'Synthetic tenant correspondence' : 'Your message';
  $('sourceText').hidden = state.editing;
  $('sourceEditorLabel').hidden = !state.editing;
  $('editThread').textContent = state.editing ? 'Show message' : 'Edit message';
  const source = $('sourceText');
  source.replaceChildren();
  const field = state.result?.fields[state.field];
  const quote = field?.quote;
  const start = quote ? state.text.indexOf(quote) : -1;
  if (start >= 0 && state.text.indexOf(quote, start + 1) < 0) {
    source.append(document.createTextNode(state.text.slice(0, start)));
    source.append(node('mark', '', quote));
    source.append(document.createTextNode(state.text.slice(start + quote.length)));
    $('sourceHelp').textContent = `Highlighted source for “${FIELD_NAMES[state.field]}”.`;
  } else {
    source.textContent = state.text;
    $('sourceHelp').textContent = field?.evidence_status === 'operator' ? 'This detail was supplied by the coordinator.' : quote ? 'This proposed passage needs an exact source link. Use Edit to attach the tenant’s words.' : 'Choose a detail on the repair brief to find its original passage.';
  }
}

function renderFields() {
  $('fields').replaceChildren();
  if (!state.result) return;
  for (const [key, name] of Object.entries(FIELD_NAMES)) {
    const field = state.result.fields[key];
    const row = node('div', `field-row ${key}${state.field === key ? ' selected' : ''}`);
    const detail = node('div');
    const label = node('button', 'field-name', name);
    label.type = 'button';
    label.addEventListener('click', () => {
      state.field = key;
      state.editing = false;
      renderSource();
      for (const item of $('fields').children) item.classList.toggle('selected', item === row);
      const mark = $('sourceText').querySelector('mark');
      if (mark) $('sourceText').scrollTop = mark.offsetTop - $('sourceText').offsetTop - 70;
    });
    detail.append(label);
    const missingText = key === 'apartment' ? 'Ask for the apartment number' : key === 'active_issue' ? state.result.fields.resolved_issue.value ? 'Tenant reports the issue resolved' : 'General correspondence for review' : key === 'requested_visit' ? 'Arrange a time with the tenant' : 'Empty in this thread';
    detail.append(node('p', `field-value${field.value ? '' : ' missing'}`, field.value || missingText));
    const proofLabels = {matched:'Exact passage found', unmatched:'Source passage needs correction', ambiguous:'Passage occurs more than once', missing:field.quote ? 'Conflicting or incomplete information' : 'Detail to be supplied', operator:'Coordinator entry'};
    if (field.value || field.quote || key === 'apartment') detail.append(node('p', `field-proof ${field.evidence_status}`, proofLabels[field.evidence_status]));
    const controls = node('div', 'field-controls');
    const edit = node('button', '', field.value ? 'Edit' : 'Add');
    edit.type = 'button';
    edit.setAttribute('aria-label', `Edit ${name}`);
    edit.addEventListener('click', () => editField(key));
    controls.append(edit);
    if (field.value) {
      const confirm = node('label', 'confirm-control');
      const input = document.createElement('input');
      input.type = 'checkbox';
      input.checked = state.approved.has(key);
      input.disabled = !['matched','operator'].includes(field.evidence_status);
      input.setAttribute('aria-label', `Confirm ${name}`);
      input.addEventListener('change', () => {
        input.checked ? state.approved.add(key) : state.approved.delete(key);
        renderReview();
      });
      confirm.append(input, document.createTextNode('Reviewed'));
      controls.append(confirm);
    }
    row.append(detail, controls);
    $('fields').append(row);
  }
}

function missingDetails() {
  const f = state.result.fields;
  if (!f.active_issue.value) return [];
  const missing = ['active_issue','property_address','apartment'].filter(key => !f[key].value);
  if (!f.requested_visit.value && f.requested_visit.quote) missing.push('requested_visit');
  return missing;
}

function draftType() {
  if (!state.result.fields.active_issue.value && state.result.fields.resolved_issue.value) return 'closure';
  if (!state.result.fields.active_issue.value) return 'general';
  return missingDetails().length ? 'clarification' : 'repair';
}

function renderReview() {
  if (!state.result) return;
  const entries = Object.entries(state.result.fields).filter(([, field]) => field.value);
  const badSources = entries.filter(([, field]) => !['matched','operator'].includes(field.evidence_status));
  const missing = missingDetails();
  const remaining = entries.filter(([key]) => !state.approved.has(key)).length;
  const type = draftType();
  $('reviewCount').textContent = `${state.approved.size} of ${entries.length} details reviewed`;
  $('confirmAll').disabled = !entries.some(([key, field]) => !state.approved.has(key) && ['matched','operator'].includes(field.evidence_status));
  $('handoffButton').disabled = remaining > 0 || badSources.length > 0 || entries.length === 0;
  $('handoffButton').textContent = {repair:'Create repair brief', clarification:'Draft clarification', closure:'Draft closure reply', general:'Create routing note'}[type];
  $('handoffHint').textContent = badSources.length ? 'Attach an exact source passage to each flagged detail.' : remaining ? 'Read the source highlights, then confirm the populated details.' : type === 'clarification' ? 'The reply asks for missing information. Visit requests stay unconfirmed.' : type === 'closure' ? 'Prepare a reply acknowledging the tenant’s resolved update.' : type === 'general' ? 'Prepare the original message for your property administration inbox.' : 'Create a copy-ready brief. Confirm the appointment in your own system.';
  $('attention').classList.toggle('ready', !badSources.length && !missing.length);
  $('attentionText').textContent = badSources.length ? `${badSources.length} source ${badSources.length === 1 ? 'link needs' : 'links need'} attention before handoff.` : missing.length ? `Still needed: ${missing.map(key => ({active_issue:'current fault', property_address:'property address', apartment:'apartment number', requested_visit:'a clear visiting window'})[key]).join(', ')}.` : type === 'closure' ? 'Resolved update. Prepare a closure reply for review.' : type === 'general' ? 'General correspondence. Review for your administration inbox.' : 'Address and current repair are present. Review for handoff.';
}

function render() {
  renderSource();
  renderFields();
  $('emptyBrief').hidden = !!state.result;
  $('reviewActions').hidden = !state.result;
  $('analyseButton').textContent = state.mode === 'live' ? 'Analyse with Apertus' : 'Load example brief';
  $('briefSubtitle').textContent = state.result ? 'Confirm the details you want to hand over.' : 'Apertus reads the thread. You decide the handoff.';
  const origin = state.result?.origin;
  $('runLabel').textContent = origin === 'live' ? `${state.result.model} · ${(state.result.elapsed_ms / 1000).toFixed(1)} s` : origin === 'recorded' ? 'Recorded Apertus 8B result' : 'Prepared example';
  if (!state.result) {
    $('attention').classList.remove('ready');
    $('attentionText').textContent = 'Analyse the message to prepare the repair brief.';
  } else renderReview();
}

async function analyse() {
  stopRequest();
  state.text = $('sourceEditor').value.replace(/\r\n?/g, '\n').trim();
  state.editing = false;
  if (!state.text) { announce('Paste a tenant message to begin.', true); return; }
  if (state.mode === 'sample') {
    if (state.text !== state.selected.text) {
      announce('To analyse this message, run HausPost with your Apertus endpoint. Choose an example to explore the review workflow here.', true);
      render();
      return;
    }
    const recorded = state.recorded[state.selected.id];
    acceptResult(recorded?.result || state.selected.example, recorded ? 'recorded' : 'example');
    announce(recorded ? 'Recorded Apertus output loaded. Review and correct it against the source.' : 'Prepared example loaded. The fields are author-written examples for exploring the workflow.');
    return;
  }
  state.result = null;
  state.approved.clear();
  render();
  const generation = state.generation;
  const controller = new AbortController();
  state.controller = controller;
  const timeout = setTimeout(() => controller.abort(), (state.timeout + 5) * 1000);
  $('analyseButton').disabled = true;
  document.body.classList.add('busy');
  $('attentionText').textContent = 'Apertus is reading the full thread…';
  announce('Analysis is running on the configured Apertus server. CPU inference can take a few minutes.');
  try {
    const response = await fetch('api/analyse', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text:state.text}), signal:state.controller.signal});
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || `Analysis failed (HTTP ${response.status}).`);
    if (generation !== state.generation) return;
    acceptResult(data, 'live');
    announce('Apertus finished. Review the exact passages and correct any detail before handoff.');
  } catch (error) {
    if (generation !== state.generation) return;
    announce(error.name === 'AbortError' ? 'Analysis timed out. Check the model server, then try again.' : error.message, true);
    $('attentionText').textContent = 'Analysis stopped. Your message is still on the desk.';
  } finally {
    clearTimeout(timeout);
    if (generation === state.generation) {
      state.controller = null;
      $('analyseButton').disabled = false;
      document.body.classList.remove('busy');
    }
  }
}

function editField(key) {
  state.field = key;
  const field = state.result.fields[key];
  $('editTitle').textContent = FIELD_NAMES[key];
  $('fieldValue').value = field.value || '';
  $('fieldQuote').value = field.quote || '';
  $('operatorEntry').checked = field.evidence_status === 'operator' || (!field.value && !field.quote);
  $('fieldQuote').disabled = $('operatorEntry').checked;
  $('editError').textContent = '';
  renderSource();
  $('editDialog').showModal();
  $('fieldValue').focus();
}

function makeDrafts() {
  const fields = state.result.fields;
  const value = key => fields[key].value || '';
  const type = draftType();
  const missing = missingDetails();
  const lines = [`HausPost — ${{repair:'Repair brief', closure:'Resolved update', clarification:'Clarification needed', general:'General correspondence'}[type]}`, '', `Prepared: ${new Date().toLocaleString()}`, `Property: ${value('property_address') || 'To be supplied'}`, `Apartment: ${value('apartment') || 'To be supplied'}`, `Tenant: ${value('contact_name') || 'To be supplied'}`, ''];
  if (value('active_issue')) lines.push(`Current repair: ${value('active_issue')}`);
  if (value('resolved_issue')) lines.push(`Reported resolved: ${value('resolved_issue')}`);
  if (value('requested_visit')) lines.push(`Tenant-requested window: ${value('requested_visit')}`, 'Appointment state: awaiting coordinator confirmation.');
  else if (['repair','clarification'].includes(type)) lines.push('Visit: arrange a time with the tenant.');
  if (value('cancelled_visit')) lines.push(`Cancelled window: ${value('cancelled_visit')}`);
  if (missing.length) lines.push('', `Ask for: ${missing.map(key => FIELD_NAMES[key]).join('; ')}.`);
  if (type === 'closure') lines.push('', 'Next action: review the tenant’s resolved update and record closure in your maintenance system.');
  if (type === 'general') lines.push('', 'Route: property administration inbox. Review the current inquiry in the original thread.', '', 'Original thread', state.text);
  lines.push('', 'Reviewed sources');
  for (const [key, field] of Object.entries(fields)) if (field.value) lines.push(`${FIELD_NAMES[key]}: ${field.evidence_status === 'operator' ? 'Coordinator entry' : `“${field.quote}”`}`);

  const language = LANGUAGES[state.result.language] ? state.result.language : 'en';
  const copy = {
    de:{hello:'Guten Tag', thanks:'Vielen Dank für Ihre Nachricht.', ask:'Bitte teilen Sie uns noch Folgendes mit: ', names:{active_issue:'den aktuell bestehenden Defekt',property_address:'die vollständige Liegenschaftsadresse',apartment:'Ihre Wohnungsnummer',requested_visit:'einen passenden Besuchszeitraum'}, window:'Ihren gewünschten Besuchszeitraum haben wir vorgemerkt.', next:'Wir melden uns zur Abstimmung und Bestätigung eines Termins.', closure:'Vielen Dank für Ihre Rückmeldung. Wir haben zur Kenntnis genommen, dass das gemeldete Problem behoben ist.', bye:'Freundliche Grüsse\nIhre Verwaltung'},
    fr:{hello:'Bonjour,', thanks:'Merci pour votre message.', ask:'Pourriez-vous nous préciser les éléments suivants : ', names:{active_issue:'le problème actuellement rencontré',property_address:'l’adresse complète de l’immeuble',apartment:'le numéro de votre appartement',requested_visit:'un créneau de visite qui vous convient'}, window:'Nous avons pris note du créneau de visite souhaité.', next:'Nous vous recontacterons pour convenir d’un rendez-vous et le confirmer.', closure:'Merci pour votre retour. Nous avons bien pris note que le problème signalé est résolu.', bye:'Meilleures salutations,\nVotre gérance'},
    it:{hello:'Buongiorno,', thanks:'Grazie per il suo messaggio.', ask:'La preghiamo di comunicarci i seguenti dettagli: ', names:{active_issue:'il guasto attualmente presente',property_address:'l’indirizzo completo dell’immobile',apartment:'il numero del suo appartamento',requested_visit:'una fascia oraria disponibile per la visita'}, window:'Abbiamo preso nota della fascia oraria da lei richiesta.', next:'La ricontatteremo per concordare e confermare l’appuntamento.', closure:'Grazie per l’aggiornamento. Abbiamo preso nota che il problema segnalato è stato risolto.', bye:'Cordiali saluti,\nLa sua amministrazione'},
    en:{hello:'Hello,', thanks:'Thank you for your message.', ask:'Please send us the following details: ', names:{active_issue:'the current fault',property_address:'the full property address',apartment:'your apartment number',requested_visit:'a suitable visiting window'}, window:'We have noted your requested visiting window.', next:'We will contact you to arrange and confirm an appointment.', closure:'Thank you for the update. We have noted that the reported problem is resolved.', bye:'Kind regards,\nYour property management team'}
  }[language];
  const generalReply = {de:'Vielen Dank für Ihre Nachricht. Wir prüfen Ihr Anliegen und melden uns bei Ihnen.',fr:'Merci pour votre message. Nous allons examiner votre demande et vous recontacter.',it:'Grazie per il suo messaggio. Esamineremo la sua richiesta e la ricontatteremo.',en:'Thank you for your message. We will review your inquiry and get back to you.'};
  const reply = [copy.hello, '', type === 'closure' ? copy.closure : type === 'general' ? generalReply[language] : copy.thanks];
  if (['repair','clarification'].includes(type)) {
    if (missing.length) reply.push('', copy.ask + missing.map(key => copy.names[key]).join(', ') + '.');
    if (value('requested_visit')) reply.push('', copy.window);
    reply.push('', copy.next);
  }
  reply.push('', copy.bye);
  return {brief:lines.join('\n'), reply:reply.join('\n'), type, language};
}

function showDraftTab(tab) {
  state.tab = tab;
  $('handoffText').textContent = state.drafts[tab];
  for (const id of ['brief','reply']) {
    $(id + 'Tab').classList.toggle('selected', id === tab);
    $(id + 'Tab').setAttribute('aria-pressed', String(id === tab));
  }
  $('copyStatus').textContent = '';
}

$('casePicker').addEventListener('change', event => chooseCase(event.target.value));
$('editThread').addEventListener('click', () => {state.editing = !state.editing;renderSource();if (state.editing) $('sourceEditor').focus();});
$('sourceEditor').addEventListener('input', () => {
  stopRequest();
  state.text = $('sourceEditor').value;
  state.result = null;
  state.approved.clear();
  announce('Message changed. Analyse it again to create a fresh brief.');
  render();
});
$('analyseButton').addEventListener('click', analyse);
$('confirmAll').addEventListener('click', () => {
  for (const [key, field] of Object.entries(state.result.fields)) if (field.value && ['matched','operator'].includes(field.evidence_status)) state.approved.add(key);
  renderFields();renderReview();
});
$('operatorEntry').addEventListener('change', () => {$('fieldQuote').disabled = $('operatorEntry').checked;});
$('editForm').addEventListener('submit', event => {
  event.preventDefault();
  const value = $('fieldValue').value.trim();
  const quote = $('fieldQuote').value.trim();
  const field = locate(value || null, quote || null, $('operatorEntry').checked);
  if (value && !['matched','operator'].includes(field.evidence_status)) {
    $('editError').textContent = field.evidence_status === 'ambiguous' ? 'This passage appears more than once. Include a longer, unique passage.' : 'Paste one exact passage from the message, or mark this as your own information.';
    return;
  }
  state.result.fields[state.field] = field;
  state.approved.delete(state.field);
  $('editDialog').close();render();
  announce('Detail saved. Review the corrected value before creating the handoff.');
});
for (const button of document.querySelectorAll('[data-close]')) button.addEventListener('click', () => $(button.dataset.close).close());
$('handoffButton').addEventListener('click', () => {
  if ($('handoffButton').disabled) return;
  state.drafts = makeDrafts();
  const type = state.drafts.type;
  $('handoffTitle').textContent = {repair:'Ready for the maintenance desk', clarification:'Ask for the missing detail', closure:'Acknowledge the resolved repair', general:'Route the current inquiry'}[type];
  $('handoffDescription').textContent = 'Copy-ready drafts. Review the wording, then send through your own system.';
  $('replyTab').textContent = `Tenant reply · ${LANGUAGES[state.drafts.language]}`;
  showDraftTab(['repair','general'].includes(type) ? 'brief' : 'reply');
  $('handoffDialog').showModal();
});
$('briefTab').addEventListener('click', () => showDraftTab('brief'));
$('replyTab').addEventListener('click', () => showDraftTab('reply'));
$('copyButton').addEventListener('click', async () => {
  try {await navigator.clipboard.writeText(state.drafts[state.tab]);$('copyStatus').textContent = 'Draft copied.';}
  catch {$('copyStatus').textContent = 'Select the draft to copy it, or download the text.';}
});
$('downloadButton').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([state.drafts[state.tab]], {type:'text/plain;charset=utf-8'}));
  const link = document.createElement('a');link.href = url;link.download = `hauspost-${state.drafts.type}-${state.tab}.txt`;link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  $('copyStatus').textContent = 'Text file downloaded.';
});

async function init() {
  try {
    const [casesResponse, recordedResponse, status] = await Promise.all([
      fetch('data/cases.json'), fetch('data/recorded-runs.json'),
      location.hostname.endsWith('.github.io') ? Promise.resolve({mode:'sample'}) : fetch('api/status').then(response => response.ok ? response.json() : {mode:'sample'}).catch(() => ({mode:'sample'}))
    ]);
    if (!casesResponse.ok) throw new Error('Example data failed to load. Refresh the page to try again.');
    state.cases = await casesResponse.json();
    state.recorded = recordedResponse.ok ? await recordedResponse.json() : {};
    state.mode = status.mode === 'live' ? 'live' : 'sample';
    state.timeout = status.model_timeout_seconds || 180;
    $('modeBadge').textContent = state.mode === 'live' ? 'Apertus connected' : 'Example mode';
    if (state.mode === 'live') $('privacyNote').textContent = 'Analysis sends this message to the Apertus endpoint configured by your operator. The on-prem profile uses the model container on your own infrastructure. This desk keeps the message in memory for the current interaction.';
    $('casePicker').replaceChildren();
    for (const item of state.cases) {const option = node('option','',`${item.language.toUpperCase()} · ${item.title}`);option.value=item.id;$('casePicker').append(option);}
    chooseCase(state.cases[0].id);
  } catch (error) {announce(error.message, true);$('modeBadge').textContent='Load failed';}
}

init();
