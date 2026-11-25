// Integrationstests: alle ECOMEX-Workflows mit der echten n8n-2.46-Engine.
const nock = require('nock');
const path = require('path');
const os = require('os');
const fs = require('fs');
const { runWorkflow, binaryItem, out, executed, WORKFLOWS, readBinary } = require('./harness');
nock.disableNetConnect();
nock.enableNetConnect('127.0.0.1');

const F = path.join(__dirname, 'fixtures') + '/';
const REPO = path.resolve(__dirname, '../../..') + '/';
const DECKDATEN = path.join(os.tmpdir(), 'ecomex-test-deckdaten.json');
const SB = 'https://test.supabase.co';
const AZ = 'https://ecomex-doc-intelligence.cognitiveservices.azure.com';
const AN = 'https://api.anthropic.com';
const RENDERER_OK = process.env.RENDERER_TEST_URL || 'http://127.0.0.1:8099';
const RENDERER_WEG = 'http://127.0.0.1:8098';
const W = n => Object.keys(WORKFLOWS).find(k => k.startsWith('ECOMEX ' + n + ' |'));

let fails = 0, passes = 0;
const ok = (c, msg) => { if (c) { passes++; console.log('  ✔ ' + msg); } else { fails++; console.log('  ✖ ' + msg); } };
const err = run => run.data.resultData.error ? (run.data.resultData.error.message + ' @ ' + (run.data.resultData.error.node || {}).name) : '';

// ---------------------------------------------------------------- Konfiguration (ECOMEX 0 › Edit Fields)
function setKonfig(values) {
  global.KONFIG_PATCH = wf => {
    const n = wf.nodes.find(x => x.name === 'Edit Fields');
    for (const a of n.parameters.assignments.assignments) if (a.name in values) a.value = values[a.name];
  };
}
const STD = { renderer_url: RENDERER_OK, supabase_url: SB, azure_di_endpoint: AZ };

// ---------------------------------------------------------------- GitHub (Regelwerk + Katalog)
const regeln = ['curriculum.md', 'didaktik.md', 'design.md', 'qa_rules.md', 'content_workflow.md'];
function githubMock({ ohneRegel } = {}) {
  const gh = nock('https://api.github.com').persist();
  gh.get(/\/repos\/ecomewb\/Ecomex-Content-Factory\/contents\/governance(\?.*)?$/).reply(200,
    [...regeln.filter(r => r !== ohneRegel), 'optional_methods'].map(n => ({ name: n, path: 'governance/' + n, type: n.endsWith('.md') ? 'file' : 'dir', sha: 'abc1234567' + n.length })));
  gh.get(/\/contents\/governance(\/|%2F)[a-z_]+\.md/).reply(uri => {
    const name = decodeURIComponent(uri.split('?')[0]).split('/').pop();
    const text = fs.readFileSync(REPO + 'governance/' + name, 'utf8');
    return [200, { name, path: 'governance/' + name, sha: 'def9876543', content: Buffer.from(text).toString('base64').replace(/(.{60})/g, '$1\n'), encoding: 'base64' }];
  });
  gh.get(/\/contents\/renderer(\/|%2F)app(\/|%2F)catalog\.json/).reply(200, { name: 'catalog.json', sha: 'cat1', encoding: 'base64',
    content: Buffer.from(fs.readFileSync(REPO + 'renderer/app/catalog.json')).toString('base64') });
  return gh;
}

// ---------------------------------------------------------------- Azure Document Intelligence
function azureMock({ fail } = {}) {
  let polls = 0;
  const az = nock(AZ);
  az.post(/\/documentintelligence\/documentModels\/prebuilt-layout:analyze/).reply(function () {
    global.AZ_HEADERS = this.req.headers;
    return [202, '', { 'operation-location': AZ + '/documentintelligence/documentModels/prebuilt-layout/analyzeResults/op1?api-version=2024-11-30' }];
  });
  az.get(/analyzeResults\/op1/).times(5).reply(() => {
    polls++;
    if (polls < 2) return [200, { status: 'running' }];
    if (fail) return [200, { status: 'failed', error: { code: 'InvalidContent', message: 'The file is corrupted or format is unsupported.' } }];
    return [200, { status: 'succeeded', analyzeResult: { content: 'Willkommen\nAgenda Punkt 1\nZweite Folie', pages: [
      { pageNumber: 1, spans: [{ offset: 0, length: 24 }] }, { pageNumber: 2, spans: [{ offset: 25, length: 12 }] }] } }];
  });
  return () => polls;
}

// ---------------------------------------------------------------- Anthropic (PPTX-Skill + Files API)
function anthropicMock({ keineDatei } = {}) {
  const bodies = [];
  const an = nock(AN);
  an.post('/v1/messages').reply(function (uri, body) {
    bodies.push({ body, headers: this.req.headers });
    return [200, { id: 'msg1', stop_reason: 'pause_turn', container: { id: 'cont_1' }, content: [{ type: 'text', text: 'Ich lege die Folien an.' }] }];
  });
  an.post('/v1/messages').reply(function (uri, body) {
    bodies.push({ body, headers: this.req.headers });
    return [200, { id: 'msg2', stop_reason: 'end_turn', container: { id: 'cont_1' }, content: keineDatei ? [{ type: 'text', text: 'Fertig' }] : [
      { type: 'bash_code_execution_tool_result', content: { type: 'bash_code_execution_result', content: [{ type: 'bash_code_execution_output', file_id: 'file_PPTX1' }] } },
      { type: 'text', text: 'Fertig. Abweichungen: keine.' }] }];
  });
  an.get('/v1/files/file_PPTX1').reply(200, { id: 'file_PPTX1', filename: 'ECOMEX_M02_Tag 12_ENTWURF.pptx', size_bytes: 1000 });
  an.get('/v1/files/file_PPTX1/content').reply(200, fs.readFileSync(F + 'deck.pptx'), { 'Content-Type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation' });
  return bodies;
}

// ---------------------------------------------------------------- Testdaten
const sample = JSON.parse(fs.readFileSync(REPO + 'renderer/tests/sample_deck.json', 'utf8'));
const katalog = JSON.parse(fs.readFileSync(REPO + 'renderer/app/catalog.json', 'utf8'));
const zeilen = [
  { Tag: 'Tag 12', Block: 1, Von: '09:00', Bis: '10:30', Titel: 'Warum KI-Workflows anders getestet werden', Art: 'input', Lernziele: 'Die TN können Fehlerbilder benennen', Folien: 8 },
  { Tag: 'Tag 12', Block: 2, Von: '10:30', Bis: '10:45', Titel: 'Pause', Art: 'pause', Folien: 1 },
  { Tag: 'Tag 12', Block: 3, Von: '10:45', Bis: '12:00', Titel: 'Übung: Testfälle bauen', Art: 'uebung', Lernziele: 'Die TN können Testfälle formulieren', Folien: 6 },
];
const inhaltFolien = sample.folien.filter(f => !['titel', 'tagesablauf', 'lernziele'].includes(f.layout));
global.SUB_OVERRIDES = {};
function wf3Fake(items) {
  return items.map(i => {
    const z = i.json.zeile;
    if (String(z.Art) === 'pause') return { json: { block: z.Block, titel: z.Titel, folien: [{ layout: 'pause', block: 'Block ' + z.Block, felder: { titel: 'Pause', dauer: '15 Min.' }, notizen: 'Pause.' }], qa: { status: 'OHNE_KI', befunde: [] }, quellen: [] } };
    const part = z.Block === 1 ? inhaltFolien.slice(0, 8) : inhaltFolien.slice(8, 14);
    return { json: { block: z.Block, titel: z.Titel, folien: part.map(f => ({ ...f, block: 'Block ' + z.Block })), qa: { status: 'OK', befunde: [{ folie: 2, schwere: 'minor', befund: 'Beispiel', korrektur: 'kürzen' }] }, quellen: [{ titel: 'Bitkom', url: 'https://bitkom.org' }] } };
  });
}

async function konfigHolen() {
  const run = await runWorkflow(W(0), [{ json: { nur_konfig: true } }]);
  return out(run, 'No Operation, do nothing')[0].json.konfig;
}
async function tagAuftrag() {
  const run = await runWorkflow(W(0), [{ json: { probe: 1 } }]);
  const r = out(run, 'No Operation, do nothing1')[0].json;
  return { run_id: 'ECX-TEST', modul: 'M02', thema: 'KI-Arbeitsabläufe testen', zielgruppe: 'Erwachsene', folien_pro_tag: 30, storyboard_titel: 'KI testen',
    erstellt_von: '', tag: 'Tag 12', zeilen, regeln: r.regeln, regel_versionen: r.regel_versionen, katalog: r.katalog, konfig: r.konfig };
}

(async () => {
  githubMock();

  // ============================================================ ECOMEX 0
  console.log('ECOMEX 0 | Konfiguration & Regelwerk');
  setKonfig(STD);
  let run = await runWorkflow(W(0), [{ json: { nur_konfig: true, titel: 'x' } }]);
  let k = out(run, 'No Operation, do nothing')[0].json;
  ok(!err(run) && k.konfig.renderer_aktiv === true && k.titel === 'x' && !executed(run).includes('List files'), 'nur_konfig + Renderer erreichbar: schnell, renderer_aktiv=true');
  setKonfig({ ...STD, renderer_url: RENDERER_WEG });
  run = await runWorkflow(W(0), [{ json: { nur_konfig: true } }]);
  k = out(run, 'No Operation, do nothing')[0].json;
  ok(k.konfig.renderer_aktiv === false && /nicht erreichbar/.test(k.konfig.renderer_status), 'Renderer weg → renderer_aktiv=false: ' + k.konfig.renderer_status.slice(0, 70));
  setKonfig({ ...STD, renderer_url: '' });
  run = await runWorkflow(W(0), [{ json: { nur_konfig: true } }]);
  ok(out(run, 'No Operation, do nothing')[0].json.konfig.renderer_aktiv === false, 'Renderer-URL leer → ohne Renderer');
  setKonfig(STD);
  run = await runWorkflow(W(0), [{ json: { probe: 1 } }]);
  const voll = out(run, 'No Operation, do nothing1');
  ok(!err(run) && voll && Object.keys(voll[0].json.regeln).length === 5 && voll[0].json.katalog.layouts.length === katalog.layouts.length && /GitHub/.test(voll[0].json.konfig.katalog_quelle),
    'voller Lauf: 5 Regeln + ' + katalog.layouts.length + ' Layouts aus GitHub (Ordner optional_methods ignoriert)');
  nock.cleanAll(); githubMock({ ohneRegel: 'qa_rules.md' });
  run = await runWorkflow(W(0), [{ json: {} }]);
  ok(/qa_rules\.md/.test(err(run)) && /Systemcheck/.test(err(run)), 'fehlende Pflichtregel → klarer Abbruch: ' + err(run).slice(0, 80));
  run = await runWorkflow(W(0), [{ json: { pruefmodus: true } }]);
  ok(!err(run) && out(run, 'No Operation, do nothing1')[0].json.regelwerk_ok === false, 'Prüfmodus: meldet Fehler statt abzubrechen');
  nock.cleanAll(); githubMock();

  // ============================================================ ECOMEX 7
  console.log('ECOMEX 7 | Text extrahieren');
  const kOn = await konfigHolen();
  setKonfig({ ...STD, renderer_url: RENDERER_WEG });
  const kOff = await konfigHolen();
  setKonfig({ ...STD, renderer_url: RENDERER_WEG, azure_di_endpoint: '' });
  const kOffNoAz = await konfigHolen();
  setKonfig(STD);
  const t7 = async (file, mime, konfig) => {
    const r = await runWorkflow(W(7), [await binaryItem({ konfig }, 'datei', F + file, mime)]);
    const o = out(r, 'No Operation, do nothing');
    return { run: r, o: o && o[0] && o[0].json, ex: executed(r) };
  };
  let t = await t7('deck.pptx', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', kOn);
  ok(!err(t.run) && t.o.extraktion === 'renderer' && t.o.source_type === 'pptx' && t.o.abschnitte_anzahl >= 20 && /Folie 1/.test(t.o.abschnitte[0].fundstelle), 'PPTX mit Renderer: ' + t.o.abschnitte_anzahl + ' Folien inkl. Notizen');
  t = await t7('deck.pdf', 'application/pdf', kOff);
  ok(t.o.extraktion === 'n8n' && t.o.abschnitte_anzahl === 24 && !t.ex.includes('HTTP Request1'), 'PDF ohne Renderer: 24 Seiten mit n8n, Azure nicht nötig');
  t = await t7('tabelle.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', kOff);
  ok(t.o.extraktion === 'n8n' && t.o.abschnitte_anzahl === 2 && /Titel: Titel 1/.test(t.o.abschnitte[0].text) && t.o.source_type === 'other', 'Excel ohne Renderer: 30 Zeilen → 2 Abschnitte, source_type other');
  t = await t7('notizen.md', 'text/markdown', kOff);
  ok(t.o.abschnitte_anzahl === 2 && t.o.source_type === 'md', 'Markdown ohne Renderer: 2 Abschnitte');
  let polls = azureMock();
  t = await t7('deck.pptx', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', kOff);
  ok(!err(t.run) && t.o.extraktion === 'azure' && t.o.abschnitte_anzahl === 2 && t.o.abschnitte[1].fundstelle === 'Folie 2' && polls() === 2, 'PPTX ohne Renderer → Azure (1× warten, dann fertig): ' + t.o.abschnitte.map(a => a.fundstelle).join(', '));
  ok(global.AZ_HEADERS['ocp-apim-subscription-key'] === 'az-test' && /presentationml/.test(global.AZ_HEADERS['content-type']), 'Azure: Header-Auth + Content-Type korrekt');
  nock.cleanAll(); githubMock(); azureMock();
  t = await t7('scan.pdf', 'application/pdf', kOff);
  ok(t.o.extraktion === 'azure' && t.ex.includes('Extract from File') && t.o.abschnitte_anzahl > 0, 'gescanntes PDF: n8n findet keinen Text → Azure');
  nock.cleanAll(); githubMock(); azureMock({ fail: true });
  t = await t7('deck.pptx', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', kOff);
  ok(t.o.abschnitte_anzahl === 0 && /InvalidContent|corrupted/.test(t.o.hinweis), 'Azure-Fehler → verständlicher Hinweis: ' + t.o.hinweis.slice(0, 80));
  t = await t7('deck.pptx', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', kOffNoAz);
  ok(t.o.abschnitte_anzahl === 0 && /als PDF speichern/.test(t.o.hinweis) && /nicht eingetragen/.test(t.o.hinweis), 'PPTX ohne Renderer und ohne Azure → Hinweis „als PDF speichern“');
  t = await t7('deck.pdf', 'application/pdf', { ...kOn, renderer_url: RENDERER_WEG });
  ok(!err(t.run) && t.o.extraktion === 'n8n' && t.o.abschnitte_anzahl === 24 && /Renderer-Fehler/.test(t.o.hinweis), 'Renderer fällt mitten im Lauf aus → n8n übernimmt, Hinweis im Ergebnis');

  // ============================================================ ECOMEX 8
  console.log('ECOMEX 8 | PPTX ohne Renderer (Claude)');
  let bodies = anthropicMock();
  const deck = { ...sample, meta: { ...sample.meta, dateiname: 'ECOMEX_M02_Tag 12_ENTWURF' } };
  run = await runWorkflow(W(8), [{ json: { deck, konfig: { ...kOff, claude_master_file_id: 'file_MASTER' }, design_regeln: '# Design', katalog } }]);
  let o8 = out(run, 'No Operation, do nothing');
  ok(!err(run) && o8[0].binary && o8[0].binary.pptx && o8[0].json.pptx_quelle === 'claude' && o8[0].json.claude_runden === 2, 'Claude: Pause → Fortsetzung → PPTX heruntergeladen (2 Runden)');
  ok(bodies[0].headers['x-api-key'] === 'sk-ant-test' && bodies[0].headers['anthropic-version'] === '2026-10-21' && bodies[0].body.container.skills[0].skill_id === 'pptx'
    && bodies[0].body.messages[0].content[1].file_id === 'file_MASTER', 'Anthropic-Header + PPTX-Skill + Master als container_upload');
  ok(bodies[1].body.container.id === 'cont_1' && bodies[1].body.messages.length === 2 && bodies[1].body.messages[1].role === 'assistant', 'Fortsetzung im selben Container mit Assistent-Inhalt');
  anthropicMock({ keineDatei: true });
  run = await runWorkflow(W(8), [{ json: { deck, konfig: kOff, design_regeln: '', katalog } }]);
  o8 = out(run, 'No Operation, do nothing');
  ok(!err(run) && o8[0].json.pptx_quelle === 'keine' && /keine PowerPoint/.test(o8[0].json.hinweis), 'Claude liefert keine Datei → sauberer Hinweis statt Absturz');
  nock(AN).post('/v1/messages').reply(529, { type: 'error', error: { type: 'overloaded_error', message: 'Overloaded' } }).persist();
  run = await runWorkflow(W(8), [{ json: { deck, konfig: kOff, design_regeln: '', katalog } }], { patch: wf => { wf.nodes.find(n => n.name === 'HTTP Request').retryOnFail = false; } });
  o8 = out(run, 'No Operation, do nothing');
  ok(!err(run) && o8[0].json.pptx_quelle === 'keine' && /Claude-API-Fehler/.test(o8[0].json.hinweis), 'Anthropic überlastet → Hinweis, Workflow läuft weiter');
  nock.cleanAll(); githubMock();

  // ============================================================ ECOMEX 2
  console.log('ECOMEX 2 | Tag produzieren');
  global.SUB_OVERRIDES[W(3)] = wf3Fake;
  setKonfig(STD);
  let auftrag = await tagAuftrag();
  run = await runWorkflow(W(2), [{ json: auftrag }]);
  let m = out(run, 'Merge');
  const namen = items => items.flatMap(i => Object.values(i.binary || {}).map(b => b.fileName));
  ok(!err(run) && m && m.length === 4, 'mit Renderer: 4 Ergebnis-Items im Merge – ' + err(run));
  const dateien = m ? namen(m) : [];
  ok(dateien.some(n => /\.pptx$/.test(n)) && dateien.some(n => /\.pdf$/.test(n)) && dateien.some(n => /QA-Bericht\.md$/.test(n)) && dateien.some(n => /Deckdaten\.json$/.test(n)) && dateien.some(n => /Manuskript\.html$/.test(n)),
    'mit Renderer: PPTX, PDF, QA-Bericht, Deckdaten, Manuskript: ' + dateien.join(', '));
  let bericht = out(run, 'Edit Fields2')[0].json.bericht;
  ok(/im ECOMEX-Originalmaster/.test(bericht) && /GESAMT: OK/.test(bericht) && /Automatische Layoutprüfung \(Renderer\)/.test(bericht), 'QA-Bericht: Renderer + visuelle Prüfung');
  const deckdaten = JSON.parse((await readBinary(m.find(i => i.binary && i.binary.data && /Deckdaten/.test(i.binary.data.fileName)).binary.data)).toString());
  fs.writeFileSync(DECKDATEN, JSON.stringify(deckdaten));
  ok(deckdaten.deck.folien.length === 3 + 8 + 1 + 6 && deckdaten.deck.meta.storyboard_zeilen.length === 3, 'Deckdaten: Rahmen + alle Blöcke (' + deckdaten.deck.folien.length + ' Folien)');

  bodies = anthropicMock();
  setKonfig({ ...STD, renderer_url: RENDERER_WEG });
  auftrag = await tagAuftrag();
  run = await runWorkflow(W(2), [{ json: auftrag }]);
  m = out(run, 'Merge');
  ok(!err(run) && m && namen(m).some(n => /\.pptx$/.test(n)) && !namen(m).some(n => /\.pdf$/.test(n)), 'ohne Renderer: PPTX über Claude, keine PDF – ' + (m ? namen(m).join(', ') : err(run)));
  bericht = out(run, 'Edit Fields2')[0].json.bericht;
  ok(/Claude-PPTX-Skill ohne Renderer/.test(bericht) && /Nicht durchgeführt \(ohne Renderer\)/.test(bericht), 'QA-Bericht nennt den Claude-Weg');
  setKonfig({ ...STD, renderer_url: RENDERER_WEG, pptx_ohne_renderer: 'aus' });
  auftrag = await tagAuftrag();
  run = await runWorkflow(W(2), [{ json: auftrag }]);
  m = out(run, 'Merge');
  ok(!err(run) && m && m.length === 4 && !namen(m).some(n => /\.pptx$/.test(n)) && /KEINE PPTX/.test(out(run, 'Edit Fields2')[0].json.bericht), 'ohne Renderer + Claude aus: Manuskript/Deckdaten/QA ohne PPTX');
  setKonfig(STD);

  // ============================================================ ECOMEX 4
  console.log('ECOMEX 4 | Deck überarbeiten');
  global.FORM_ANTWORTEN = {};
  const form4 = async (aktion, block) => binaryItem({ aktion, block, hinweise: 'kürzer', freigabe: ['ok'] }, 'deckdaten', DECKDATEN, 'application/json');
  run = await runWorkflow(W(4), [await form4('Nur neu rendern', '')]);
  let f = out(run, 'Form');
  ok(!err(run) && f && /\.zip$/.test(f[0].json.datei) && /neue PPTX/.test(f[0].json.meldung), 'Nur neu rendern (Renderer): ZIP mit PPTX + Deckdaten – ' + err(run));
  run = await runWorkflow(W(4), [await form4('Block neu erzeugen', 3)]);
  f = out(run, 'Form');
  const neu = out(run, 'Edit Fields2')[0].json.deck;
  ok(!err(run) && f && neu.meta.revisionen.length === 1 && neu.folien.filter(x => x.block === 'Block 3').length === 6, 'Block 3 neu erzeugen: eingesetzt + Revision vermerkt');
  run = await runWorkflow(W(4), [await form4('Block neu erzeugen', 9)]);
  ok(/Block 9 ist in den Deckdaten nicht enthalten/.test(err(run)), 'unbekannter Block → klare Meldung');
  anthropicMock();
  setKonfig({ ...STD, renderer_url: RENDERER_WEG });
  run = await runWorkflow(W(4), [await form4('Nur neu rendern', '')]);
  f = out(run, 'Form');
  ok(!err(run) && f && /neue PPTX/.test(f[0].json.meldung), 'ohne Renderer: PPTX über Claude im ZIP');
  setKonfig({ ...STD, renderer_url: RENDERER_WEG, pptx_ohne_renderer: 'aus' });
  run = await runWorkflow(W(4), [await form4('Nur neu rendern', '')]);
  f = out(run, 'Form');
  ok(!err(run) && f && /keine PPTX/.test(f[0].json.meldung), 'ohne Renderer + Claude aus: ZIP nur mit Deckdaten, Meldung erklärt es');
  setKonfig(STD);

  // ============================================================ ECOMEX 5
  console.log('ECOMEX 5 | Wissensbasis befüllen');
  const supa = nock(SB).persist();
  let upload = null, row = null;
  supa.get(/\/rest\/v1\/ecomex_sources/).reply(200, []);
  supa.post(/\/storage\/v1\/object\/ecomex-sources\/Uploads\//).reply(function (uri, body) { upload = { uri, len: this.req.headers['content-length'], auth: this.req.headers.apikey }; return [200, { Key: 'ecomex-sources' + decodeURIComponent(uri.replace('/storage/v1/object/ecomex-sources', '')), Id: 'u1' }]; });
  supa.post(/\/rest\/v1\/ecomex_sources/).reply((uri, body) => { row = Array.isArray(body) ? body[0] : body; return [201, [{ ...row, id: 'r1' }]]; });
  global.VS_LOG = [];
  const form5 = async (file, mime) => binaryItem({ titel: ' Leitfaden KI ', version: '2026-11', modul: 'M02', link: '', status: 'reference – Referenz (Agenten dürfen nutzen, keine Freigabe)', zugriff: 'internal – intern', lizenz: 'ECOMEX intern', freigabe: ['ok'] }, 'datei', F + file, mime);
  run = await runWorkflow(W(5), [await form5('deck.pdf', 'application/pdf')]);
  f = out(run, 'Form2');
  ok(!err(run) && f && /24 Abschnitte/.test(f[0].json.meldung) && /supabase:\/\/ecomex-sources\/Uploads\//.test(f[0].json.meldung), 'PDF importiert: ' + (f ? f[0].json.meldung.slice(0, 110) : err(run)));
  ok(upload && upload.auth === 'sb-secret-test' && Number(upload.len) > 300000, 'Original in die Ablage hochgeladen (Supabase-Credential, ganze Datei)');
  ok(row && row.source_type === 'pdf' && row.storage_provider === 'supabase_storage' && /^[a-f0-9]{64}$/.test(row.sha256) && row.review_status === 'reference' && row.access_class === 'internal' && row.title === 'Leitfaden KI',
    'Quelle DB-konform: ' + JSON.stringify({ t: row && row.source_type, p: row && row.storage_provider, s: row && row.review_status }));
  ok(global.VS_LOG.length === 1 && global.VS_LOG[0].items.length === 24, '24 Abschnitte an den Vektorspeicher');
  nock.cleanAll(); githubMock();
  nock(SB).get(/\/rest\/v1\/ecomex_sources/).reply(200, [{ source_id: 'ECO-ALT', title: 'Alt', review_status: 'approved' }]);
  run = await runWorkflow(W(5), [await form5('deck.pdf', 'application/pdf')]);
  f = out(run, 'Form');
  ok(!err(run) && f && /bereits in der Wissensbasis/.test(f[0].json.meldung) && !executed(run).includes('HTTP Request'), 'Duplikat erkannt → nichts hochgeladen');
  nock.cleanAll(); githubMock();

  // ============================================================ ECOMEX 6
  console.log('ECOMEX 6 | Freigabe & Ablage');
  const form6 = (e) => binaryItem({ pruefer: 'Philipp', entscheidung: e, version: 'v1_0', kommentar: '' }, 'deck', F + 'deck.pptx', 'application/vnd.openxmlformats-officedocument.presentationml.presentation');
  run = await runWorkflow(W(6), [await form6('Freigegeben – veröffentlichen')]);
  f = out(run, 'Form');
  ok(!err(run) && f && /FREIGEGEBEN\.pptx$/.test(f[0].json.datei), 'mit Renderer: freigegebene Datei ' + (f && f[0].json.datei));
  setKonfig({ ...STD, renderer_url: RENDERER_WEG });
  run = await runWorkflow(W(6), [await form6('Freigegeben – veröffentlichen')]);
  f = out(run, 'Form1');
  ok(!err(run) && f && f[0].json.datei === 'deck.pptx' && /ENTWURF-Kennzeichnung in PowerPoint löschen/.test(f[0].json.meldung), 'ohne Renderer: Datei zurück + Anleitung');
  run = await runWorkflow(W(6), [await form6('Überarbeitung nötig – nicht veröffentlichen')]);
  ok(!err(run) && out(run, 'Form3'), 'Überarbeitung nötig → nichts veröffentlicht');
  setKonfig(STD);

  // ============================================================ ECOMEX 9
  console.log('ECOMEX 9 | Master an Claude');
  let up9 = null;
  nock(AN).post('/v1/files').reply(function (uri, body) { up9 = { ct: this.req.headers['content-type'], key: this.req.headers['x-api-key'], v: this.req.headers['anthropic-version'] }; return [200, { id: 'file_MASTER62', filename: 'ECOMEX_Masterlayout_6.2.pptx' }]; });
  run = await runWorkflow(W(9), [await binaryItem({ freigabe: ['ok'] }, 'master', F + 'deck.pptx', 'application/vnd.openxmlformats-officedocument.presentationml.presentation')]);
  f = out(run, 'Form');
  ok(!err(run) && f && /file_MASTER62/.test(f[0].json.meldung) && up9 && /multipart\/form-data/.test(up9.ct) && up9.key === 'sk-ant-test', 'Master hochgeladen (multipart, Anthropic-Header): ' + (f && f[0].json.meldung.slice(0, 60)));

  // ============================================================ ECOMEX 10
  console.log('ECOMEX 10 | Ablage einlesen');
  const inv = [
    { object_path: 'Referenzdecks/KI Strategie/Bitkom Leitfaden.pdf', folder: 'Referenzdecks/KI Strategie', file_name: 'Bitkom Leitfaden.pdf', extension: 'pdf', bytes: 347218, empfohlen: true, grund: 'neu', storage_uri: 'supabase://ecomex-sources/Referenzdecks/KI Strategie/Bitkom Leitfaden.pdf', source_id_vorschlag: 'SB-aaa', source_type: 'pdf', registered: false, updated_at: '2026-11-19T10:00:00Z' },
    { object_path: 'Referenzdecks/Coaching/KI_Coach.pptx', folder: 'Referenzdecks/Coaching', file_name: 'KI_Coach.pptx', bytes: 201300706, empfohlen: true, grund: 'neu' },
    { object_path: 'Referenzdecks/Mastervorlage/ECOMEX_Masterlayout_6.2.pptx', bytes: 26844796, empfohlen: false, grund: 'Folienmaster – Vorlage, keine Wissensquelle' },
    { object_path: 'Referenzdecks/Notizen/kaputt.pdf', folder: 'Referenzdecks/Notizen', file_name: 'kaputt.pdf', extension: 'pdf', bytes: 9591, empfohlen: true, grund: 'neu', storage_uri: 'supabase://ecomex-sources/Referenzdecks/Notizen/kaputt.pdf', source_id_vorschlag: 'SB-bbb', source_type: 'pdf', registered: false },
  ];
  const rows10 = [];
  const s10 = nock(SB).persist();
  s10.post('/rest/v1/rpc/ecomex_storage_inventory').reply(200, inv);
  s10.get('/storage/v1/object/ecomex-sources/Referenzdecks/KI%20Strategie/Bitkom%20Leitfaden.pdf').reply(200, fs.readFileSync(F + 'deck.pdf'), { 'Content-Type': 'application/pdf' });
  s10.get('/storage/v1/object/ecomex-sources/Referenzdecks/Notizen/kaputt.pdf').reply(404, { statusCode: '404', error: 'not_found', message: 'Object not found' });
  s10.post(/\/rest\/v1\/ecomex_sources/).reply((u, b) => { const r = Array.isArray(b) ? b[0] : b; rows10.push(r); return [201, [r]]; });
  s10.post('/rest/v1/rpc/ecomex_kb_status').reply(200, [{ review_status: 'reference', quellen: 1, quellen_ohne_text: 0, chunks: 24 }]);
  global.VS_LOG = [];
  setKonfig({ ...STD, renderer_url: RENDERER_WEG });
  run = await runWorkflow(W(10), [{ json: {} }]);
  const b10 = out(run, 'Edit Fields7');
  ok(!err(run) && b10 && b10[0].json.eingelesen === 1 && b10[0].json.fehler === 1, 'Ablage: 1 eingelesen, 1 Fehler (Download 404) – ' + err(run));
  ok(b10 && /Zu groß/.test(b10[0].json.bericht) && /KI_Coach\.pptx \(192 MB\)/.test(b10[0].json.bericht) && /Folienmaster/.test(b10[0].json.bericht) && /reference: 1 Quellen, 24 Abschnitte/.test(b10[0].json.bericht), 'Bericht: zu groß, ausgeschlossen, DB-Stand');
  ok(rows10.length === 1 && rows10[0].source_id === 'SB-aaa' && rows10[0].title === 'KI Strategie – Bitkom Leitfaden' && rows10[0].storage_provider === 'supabase_storage', 'Quelle aus der Ablage registriert: ' + (rows10[0] || {}).title);
  ok(global.VS_LOG.length === 1 && global.VS_LOG[0].items.length === 24, '24 Abschnitte in den Vektorspeicher');
  run = await runWorkflow(W(10), [{ json: {} }], { patch: wf => { wf.nodes.find(n => n.name === 'Edit Fields').parameters.assignments.assignments.find(a => a.name === 'probelauf').value = true; } });
  const p10 = out(run, 'Edit Fields7');
  ok(!err(run) && p10 && /PROBELAUF/.test(p10[0].json.bericht) && /Würde eingelesen/.test(p10[0].json.bericht) && !executed(run).includes('HTTP Request1'), 'Probelauf: nur Bericht, nichts geladen');
  nock.cleanAll(); githubMock();
  setKonfig(STD);

  // ============================================================ ECOMEX 11
  console.log('ECOMEX 11 | Systemcheck');
  const s11 = nock(SB).persist();
  s11.post('/rest/v1/rpc/ecomex_kb_status').reply(200, [{ review_status: 'reference', quellen: 12, quellen_ohne_text: 0, chunks: 800 }]);
  nock(AN).get(/\/v1\/models/).reply(200, { data: [{ id: 'claude-sonnet-5-5' }] });
  nock(AZ).get(/\/documentintelligence\/documentModels\?api-version=2024-11-30/).reply(200, { value: [{ modelId: 'prebuilt-layout' }] });
  run = await runWorkflow(W(11), [{ json: {} }]);
  let sc = out(run, 'Edit Fields3');
  ok(!err(run) && sc && sc[0].json.alles_bereit === true, 'Systemcheck: alles bereit – ' + (sc ? sc[0].json.offen + ' offen' : err(run)));
  if (sc && !sc[0].json.alles_bereit) console.log(sc[0].json.bericht);
  nock.cleanAll(); githubMock();
  nock(SB).post('/rest/v1/rpc/ecomex_kb_status').reply(404, { code: 'PGRST202', message: 'Could not find the function public.ecomex_kb_status without parameters in the schema cache' });
  nock(AN).get(/\/v1\/models/).reply(401, { type: 'error', error: { type: 'authentication_error', message: 'invalid x-api-key' } });
  nock(AZ).get(/documentModels/).reply(401, { error: { code: '401', message: 'Access denied due to invalid subscription key' } });
  global.LLM_ANTWORTEN = { [W(11) + '/Basic LLM Chain1']: { __fehler: 'Credentials could not be decrypted / not found' } };
  run = await runWorkflow(W(11), [{ json: {} }]);
  sc = out(run, 'Edit Fields3');
  ok(!err(run) && sc && sc[0].json.offen === 4 && /003_content_factory_betrieb/.test(sc[0].json.bericht) && /„Anthropic“/.test(sc[0].json.bericht), 'Systemcheck findet 4 Probleme mit Handlungsanweisung');
  console.log(sc[0].json.bericht.split('\n').filter(l => /✖/.test(l)).map(l => '      ' + l.slice(0, 160)).join('\n'));
  global.LLM_ANTWORTEN = {};
  nock.cleanAll(); githubMock();

  // ============================================================ ECOMEX 1
  console.log('ECOMEX 1 | Neues Kursdeck');
  global.SUB_CALLS = [];
  global.SUB_OVERRIDES[W(2)] = items => items.map(i => ({ json: { gestartet: i.json.tag } }));
  const form1 = async (ausgangslage, file, mime) => {
    const json = { modul: 'M02', tage: 'Tag 12', thema: 'KI testen', zielgruppe: '', ausgangslage, briefing: 'Fokus Praxis', folien_pro_tag: 30, freigabe: ['ok'] };
    return file ? binaryItem(json, 'datei', F + file, mime) : { json };
  };
  run = await runWorkflow(W(1), [await form1('C – Freigegebenes ECOMEX-Storyboard (Excel-Vorlage) direkt produzieren', 'tabelle.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')]);
  f = out(run, 'Form1');
  const c2 = global.SUB_CALLS.filter(c => c.name === W(2));
  ok(!err(run) && f && /Produktion gestartet/.test(f[0].json.titel) && c2.length === 1 && c2[0].wait === false && /\.xlsx$/.test(f[0].json.datei), 'Pfad C (Excel): Tag 12 gestartet (im Hintergrund), Storyboard-Excel zurück – ' + err(run));
  global.FORM_ANTWORTEN = { Form: { entscheidung: 'Freigeben und Produktion starten', aenderungen: '' } };
  global.LLM_ANTWORTEN = { [W(1) + '/Basic LLM Chain']: { output: { titel: 'KI testen', zusammenfassung: 'Lernreise', annahmen: [], offene_fragen: [], bloecke: zeilen } } };
  global.SUB_CALLS = [];
  setKonfig({ ...STD, renderer_url: RENDERER_WEG });
  run = await runWorkflow(W(1), [await form1('A – Vorhandenes Storyboard (Word/Excel/PDF) auswerten', 'notizen.md', 'text/markdown')]);
  f = out(run, 'Form1');
  ok(!err(run) && f && global.SUB_CALLS.some(c => c.name === W(7)) && global.SUB_CALLS.some(c => c.name === W(2)), 'Pfad A (Datei, ohne Renderer): ECOMEX 7 liest, Storyboard freigegeben, Produktion gestartet – ' + err(run));
  global.SUB_CALLS = [];
  run = await runWorkflow(W(1), [await form1('B – Storyboard aus Idee entwickeln')]);
  ok(!err(run) && out(run, 'Form1') && !global.SUB_CALLS.some(c => c.name === W(7)), 'Pfad B (Idee ohne Datei): kein Textauszug nötig');

  // ============================================================ ECOMEX 3 (Agenten-Kette, KI simuliert)
  console.log('ECOMEX 3 | Block produzieren (Ablauf, KI simuliert)');
  setKonfig(STD);
  const basis = await tagAuftrag();
  const W3 = W(3);
  const block = { ...basis, zeile: zeilen[0], tagesuebersicht: 'Block 1 …' };
  const lay = { folien: inhaltFolien.slice(0, 6).map(f => ({ layout: f.layout, felder: f.felder, notizen: f.notizen || 'Notiz' })) };
  global.LLM_ANTWORTEN = {
    [W3 + '/Basic LLM Chain']: { output: { kernaussagen: [{ aussage: 'A' }], quellen: [{ titel: 'EU AI Act', url: 'https://eur-lex.europa.eu' }] } },
    [W3 + '/Basic LLM Chain1']: { output: { folien: [{ nr: 1, funktion: 'einstieg', titel: 'T', inhalt: ['x'], notizen: 'n' }], offene_punkte: ['Screenshot fehlt'] } },
    [W3 + '/Basic LLM Chain2']: { output: lay },
    [W3 + '/Basic LLM Chain3']: { output: { status: 'OK', befunde: [], offene_punkte: [] } },
  };
  global.VS_LOG = [];
  run = await runWorkflow(W3, [{ json: block }]);
  let b3 = out(run, 'Edit Fields2');
  ok(!err(run) && b3 && b3[0].json.folien.length === 6 && b3[0].json.folien.every(x => x.block === 'Block 1') && b3[0].json.qa.status === 'OK' && b3[0].json.interne_fundstellen === 1 && !executed(run).includes('Basic LLM Chain4'),
    'QA OK: 6 Folien, Quellen, 1 interne Fundstelle, keine Revision – ' + err(run));
  const vsq = global.VS_LOG.find(v => v.load);
  ok(vsq && /Warum KI-Workflows/.test(vsq.load) && vsq.filter.metadata.metadataValues[0].value === 'true', 'Wissensbasis-Suche mit Blockthema und allow_reference=true');
  const pr = global.PROMPTS[W3 + '/Basic LLM Chain2'];
  ok(pr && /LAYOUTKATALOG/.test(pr.system) && pr.system.includes('"id":"kapitel"') && /design/i.test(pr.system) && pr.system.length > 5000, 'Layout-Agent bekommt Katalog + design.md (' + (pr ? pr.system.length : 0) + ' Zeichen)');
  ok(/Bitkom Leitfaden · Seite 3/.test(global.PROMPTS[W3 + '/Basic LLM Chain'].prompt), 'Recherche-Agent bekommt interne Fundstellen mit Fundort');
  global.LLM_ANTWORTEN[W3 + '/Basic LLM Chain3'] = { output: { status: 'UEBERARBEITEN', befunde: [{ folie: 2, schwere: 'major', befund: 'veraltet', korrektur: 'aktualisieren' }] } };
  global.LLM_ANTWORTEN[W3 + '/Basic LLM Chain4'] = { output: { folien: lay.folien.slice(0, 5), nicht_behoben: ['Quelle fehlt'] } };
  run = await runWorkflow(W3, [{ json: block }]);
  b3 = out(run, 'Edit Fields2');
  ok(!err(run) && b3[0].json.qa.status === 'UEBERARBEITET' && b3[0].json.folien.length === 5 && b3[0].json.qa.nicht_behoben.length === 1, 'QA bemängelt → Revision, nicht Behobenes bleibt sichtbar');
  run = await runWorkflow(W3, [{ json: { ...basis, zeile: zeilen[1] } }]);
  b3 = out(run, 'Edit Fields');
  ok(!err(run) && b3[0].json.folien[0].layout === 'pause' && b3[0].json.folien[0].felder.dauer === '15 Min.' && !executed(run).includes('Basic LLM Chain'), 'Pause ohne KI (15 Min.)');
  global.LLM_ANTWORTEN = {};

  // ============================================================ ECOMEX 2: Block-Ausfall + Renderer fällt beim PPTX aus
  console.log('ECOMEX 2 | Ausfälle');
  global.SUB_OVERRIDES[W(3)] = items => wf3Fake(items).map((x, i) => items[i].json.zeile.Block === 3 ? { json: { error: 'Timeout im Agenten-Team' } } : x);
  setKonfig({ ...STD, renderer_url: 'http://ecomex-renderer:8080' });
  const rm = nock('http://ecomex-renderer:8080').persist();
  rm.get('/health').reply(200, { status: 'ok', master: 'ECOMEX_Masterlayout_6.2.pptx', demo_master: false, katalog_version: '4.0' });
  rm.post('/render').query({ format: 'report' }).reply(200, { folien: 15, warnungen: [], warnungen_anzahl: 0, kritisch: 0, demo_master: false });
  rm.post('/render').query({ format: 'pptx' }).reply(500, { detail: 'LibreOffice abgestürzt' });
  anthropicMock();
  auftrag = await tagAuftrag();
  run = await runWorkflow(W(2), [{ json: auftrag }]);
  m = out(run, 'Merge');
  bericht = out(run, 'Edit Fields2') && out(run, 'Edit Fields2')[0].json.bericht;
  const deck2 = out(run, 'Edit Fields1')[0].json.deck;
  ok(!err(run) && m && namen(m).some(n => /\.pptx$/.test(n)) && /Claude-PPTX-Skill/.test(bericht), 'Renderer-PPTX scheitert → automatisch Claude-Weg – ' + err(run));
  if (!/FEHLER: Timeout/.test(bericht)) console.log(bericht.split('\n').filter(l => /Block|FEHLER/.test(l)).slice(0, 12).join('\n'), JSON.stringify(deck2.folien.filter(f => f.review_hinweise)).slice(0, 300));
  ok(deck2.folien.some(f => (f.review_hinweise || []).includes('Block fehlt – neu erzeugen')) && /FEHLER: Timeout im Agenten-Team/.test(bericht), 'ausgefallener Block → Platzhalterfolie + im QA-Bericht');
  nock.cleanAll(); githubMock();
  global.SUB_OVERRIDES[W(3)] = wf3Fake;
  setKonfig(STD);

  console.log(fails ? '\n✖ ' + fails + ' Fehler, ' + passes + ' bestanden' : '\nAlle ' + passes + ' Integrationstests bestanden.');
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error('ABBRUCH', e); process.exit(2); });
