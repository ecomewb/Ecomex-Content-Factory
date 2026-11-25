// Tests der Workflow-Ausdrücke mit der echten n8n-Expression-Engine (ohne laufendes n8n).
// Einmalig: cd tools/tests && npm install --ignore-scripts   ·   Start: node test_workflows.js
require('./stub.js');
const fs = require('fs');
const { Workflow } = require('n8n-workflow');
const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const W = path.join(ROOT, 'workflows') + '/';
const load = f => JSON.parse(fs.readFileSync(W + f, 'utf8'));
const nodeTypes = { getByName: () => ({ description: { properties: [], inputs: ['main'], outputs: ['main'] } }),
  getByNameAndVersion: () => ({ description: { properties: [], inputs: ['main'], outputs: ['main'] } }), getKnownTypes: () => ({}) };

// runSpec: { Node: [ run0, run1, ... ] }, run = [ branch0Items, branch1Items ], item = {json, binary?} oder plain json
function rd(runSpec) {
  const out = { resultData: { runData: {} } };
  for (const [n, runs] of Object.entries(runSpec)) {
    out.resultData.runData[n] = runs.map(run => ({ startTime: 0, executionTime: 0, source: [],
      data: { main: run.map(items => items.map(it => (it && it.json ? it : { json: it }))) } }));
  }
  return out;
}
function ev(wf, nodeName, path, runSpec, input) {
  const w = new Workflow({ id: '1', name: wf.name, nodes: JSON.parse(JSON.stringify(wf.nodes)), connections: wf.connections, active: false, nodeTypes, settings: wf.settings });
  const node = wf.nodes.find(n => n.name === nodeName);
  if (!node) throw new Error('Node fehlt: ' + nodeName);
  let val = node.parameters; for (const k of path) val = val[k];
  const inp = [input && input.json ? input : { json: input || {} }];
  const r = w.expression.getParameterValue(val, rd(runSpec), 0, 0, nodeName, inp, 'manual', { $execution: { id: '4711' } }, { node, data: { main: [inp] }, source: null });
  return typeof r === 'string' && /^[\[{]/.test(r.trim()) ? JSON.parse(r) : r;
}
let fails = 0;
const ok = (c, msg) => { if (!c) { fails++; console.log('  ✖ ' + msg); } else console.log('  ✔ ' + msg); };
const assignVal = (wf, node, name) => { const n = wf.nodes.find(x => x.name === node); const i = n.parameters.assignments.assignments.findIndex(a => a.name === name); return ['assignments', 'assignments', i, 'value']; };

// ---------------------------------------------------------------- WF0
console.log('WF0 Konfiguration');
const wf0 = load('00_ECOMEX_Regelwerk_und_Katalog_laden.json');
const cfg = Object.fromEntries(wf0.nodes.find(n => n.name === 'Edit Fields').parameters.assignments.assignments.map(a => [a.name, a.value]));
const base0 = { 'Edit Fields': [[[cfg]]], 'When Executed by Another Workflow': [[[{ nur_konfig: true, titel: 'X' }]]] };
let k = ev(wf0, 'Edit Fields1', ['jsonOutput'], base0, { statusCode: 200, body: { status: 'ok', master: 'ecomex_master.pptx', demo_master: false, katalog_version: '4' } });
ok(k.konfig.renderer_aktiv === true && k.titel === 'X' && k.nur_konfig === true, 'Renderer erreichbar → renderer_aktiv true, Aufrufer-Daten bleiben');
k = ev(wf0, 'Edit Fields1', ['jsonOutput'], base0, { error: { message: 'getaddrinfo ENOTFOUND ecomex-renderer' } });
ok(k.konfig.renderer_aktiv === false && /ENOTFOUND/.test(k.konfig.renderer_status), 'Renderer weg → renderer_aktiv false mit Grund: ' + k.konfig.renderer_status);
const url = ev(wf0, 'HTTP Request', ['url'], {}, { renderer_url: '' });
ok(/invalid/.test(url), 'leere Renderer-URL → sichere Ersatz-URL');
ok(ev(wf0, 'HTTP Request', ['url'], {}, { renderer_url: 'http://ecomex-renderer:8080/ ' }) === 'http://ecomex-renderer:8080/health', 'Renderer-URL wird bereinigt');
const kat = JSON.parse(fs.readFileSync(path.join(ROOT, 'renderer/app/catalog.json'), 'utf8'));
const b64 = Buffer.from(JSON.stringify(kat)).toString('base64').replace(/(.{60})/g, '$1\n');
const k1 = { ...k, konfig: { ...k.konfig, renderer_aktiv: true, renderer_katalog_version: '3', katalog_pfad: 'renderer/app/catalog.json' } };
const regeln = ['curriculum.md', 'didaktik.md', 'design.md', 'qa_rules.md', 'content_workflow.md'].map(d => ({ datei: d, sha: 'abc1234def', text: 'x'.repeat(300) }));
const LF = { 'List files': [[[{ name: 'curriculum.md', type: 'file' }]]] };
let r3 = ev(wf0, 'Edit Fields3', ['jsonOutput'], { ...LF, 'Edit Fields1': [[[k1]]], Aggregate: [[[{ regeldateien: regeln }]]], 'Get a file1': [[[{ content: b64 }]]] }, {});
ok(r3.katalog.layouts.length === kat.layouts.length && /GitHub/.test(r3.konfig.katalog_quelle), 'Katalog aus GitHub (Base64 mit Zeilenumbrüchen) gelesen: ' + r3.katalog.layouts.length + ' Layouts');
ok(/weicht/.test(r3.konfig.katalog_warnung), 'abweichende Katalogversion wird gewarnt');
ok(Object.keys(r3.regeln).length === 5 && r3.regel_versionen[0].sha === 'abc1234', 'Regeln + SHA gebündelt');
r3 = ev(wf0, 'Edit Fields3', ['jsonOutput'], { ...LF, 'Edit Fields1': [[[k1]]], Aggregate: [[[{ regeldateien: regeln }]]], 'Get a file1': [[[{ error: 'not found' }]]], 'HTTP Request1': [[[kat]]] }, {});
ok(r3.katalog.layouts.length === kat.layouts.length && /Renderer/.test(r3.konfig.katalog_quelle), 'Ersatz: Katalog vom Renderer');
ok(r3.regelwerk_ok === true && ev(wf0, 'If2', ['conditions', 'conditions', 0, 'leftValue'], {}, r3) === true, 'Pflichtregeln-Prüfung besteht');
const r4 = ev(wf0, 'Edit Fields3', ['jsonOutput'], { 'List files': [[[{ error: { message: 'The resource you are requesting could not be found' } }]]], 'Edit Fields1': [[[k1]]], Aggregate: [[[{ regeldateien: [] }]]], 'Get a file1': [[[{ error: 'x' }]]] }, {});
ok(r4.regelwerk_ok === false && /GitHub nicht erreichbar/.test(r4.regelwerk_fehler) && /Pflichtregeln fehlen/.test(r4.regelwerk_fehler), 'GitHub-Fehler wird verständlich gemeldet: ' + r4.regelwerk_fehler.slice(0, 70));
ok(ev(wf0, 'If1', ['conditions', 'conditions', 0, 'leftValue'], { 'Edit Fields1': [[[{ konfig: { renderer_aktiv: false } }]]] }, { error: 'x' }) === true, 'ohne Renderer kein Katalog-Ersatzaufruf');
ok(k.konfig.azure_aktiv === true && /cognitiveservices/.test(k.konfig.azure_di_endpoint), 'Azure-Endpunkt aus der Konfiguration');

// ---------------------------------------------------------------- WF7
console.log('WF7 Text extrahieren');
const wf7 = load('07_ECOMEX_Text_extrahieren.json');
const ef = { json: { dateiname: 'Leitfaden.PDF', konfig: { renderer_aktiv: false } }, binary: { datei: { fileName: 'Leitfaden.PDF', mimeType: 'application/pdf' } } };
ok(ev(wf7, 'Edit Fields', assignVal(wf7, 'Edit Fields', 'endung'), {}, ef) === 'pdf', 'Endung aus Dateiname (Großschreibung egal)');
const sel = { dateiname: 'Leitfaden.PDF', endung: 'pdf', renderer_aktiv: false };
let ab = ev(wf7, 'Edit Fields3', assignVal(wf7, 'Edit Fields3', 'abschnitte'), {}, { text: ['Seite eins', '', 'Seite drei'], numpages: 3 });
ok(ab.length === 3 && ab[2].fundstelle === 'Seite 3', 'PDF: je Seite ein Abschnitt');
ab = ev(wf7, 'Edit Fields4', assignVal(wf7, 'Edit Fields4', 'abschnitte'), {}, { zeilen: Array.from({ length: 30 }, (_, i) => ({ Tag: 'Tag 12', Block: i + 1, Titel: 'T' + i, Leer: '' })) });
ok(ab.length === 2 && ab[0].fundstelle === 'Zeilen 2–26' && !/Leer/.test(ab[0].text), 'Excel: 25 Zeilen je Abschnitt, leere Felder weg');
ab = ev(wf7, 'Edit Fields5', assignVal(wf7, 'Edit Fields5', 'abschnitte'), {}, { inhalt: 'Vorwort\n# Kapitel 1\nText A\n## Unterpunkt\nText B' });
ok(ab.length === 3 && /Kapitel 1/.test(ab[1].fundstelle), 'Markdown: Abschnitte an Überschriften');
const fin = ev(wf7, 'Edit Fields7', ['jsonOutput'], { 'Edit Fields': [[[sel]]] }, { abschnitte: [{ fundstelle: 'Seite 1', text: ' Hallo ' }, { fundstelle: 'Seite 2', text: '  ' }], extraktion: 'n8n' });
ok(fin.abschnitte_anzahl === 1 && fin.source_type === 'pdf' && fin.zeichen > 0 && fin.hinweis === '', 'einheitliches Ergebnis, leere Seiten entfernt');
const fin2 = ev(wf7, 'Edit Fields7', ['jsonOutput'], { 'Edit Fields': [[[{ ...sel, endung: 'xlsx' }]]] }, { abschnitte: [], hinweis: '' });
ok(fin2.source_type === 'other' && /Kein lesbarer Text/.test(fin2.hinweis), 'xlsx → source_type other (DB-konform), Hinweis bei leerem Text');
ok(ev(wf7, 'Edit Fields6', assignVal(wf7, 'Edit Fields6', 'hinweis'), {}, { endung: 'pptx' }).includes('als PDF'), 'PPTX ohne Renderer → klarer Hinweis');

const azr = { status: 'succeeded', analyzeResult: { content: 'Titel A\nPunkt 1\nTitel B', pages: [{ pageNumber: 1, spans: [{ offset: 0, length: 16 }] }, { pageNumber: 2, spans: [{ offset: 16, length: 7 }] }] } };
const az = ev(wf7, 'Edit Fields9', ['jsonOutput'], { 'Edit Fields': [[[{ ...sel, endung: 'pptx' }]]] }, azr);
ok(az.abschnitte.length === 2 && az.abschnitte[1].fundstelle === 'Folie 2' && az.abschnitte[1].text === 'Titel B' && az.extraktion === 'azure', 'Azure: Text je Folie aus spans');
const az2 = ev(wf7, 'Edit Fields9', ['jsonOutput'], { 'Edit Fields': [[[{ ...sel, endung: 'pdf' }]]] }, { analyzeResult: { content: 'x', pages: [{ pageNumber: 1, lines: [{ content: 'Zeile 1' }, { content: 'Zeile 2' }] }] } });
ok(az2.abschnitte[0].fundstelle === 'Seite 1' && az2.abschnitte[0].text === 'Zeile 1\nZeile 2', 'Azure: gescanntes PDF je Seite aus lines');
ok(/Zeitlimit/.test(ev(wf7, 'Edit Fields10', ['jsonOutput'], {}, { status: 'running' }).hinweis) && /InvalidRequest/.test(ev(wf7, 'Edit Fields10', ['jsonOutput'], {}, { status: 'failed', error: { code: 'InvalidRequest', message: 'InvalidRequest: bad file' } }).hinweis), 'Azure-Fehler und Zeitlimit verständlich');
ok(ev(wf7, 'Edit Fields8', assignVal(wf7, 'Edit Fields8', 'operation_url'), {}, { statusCode: 202, headers: { 'operation-location': 'https://ecomex-doc-intelligence.cognitiveservices.azure.com/documentintelligence/documentModels/prebuilt-layout/analyzeResults/abc?api-version=2024-11-30' } }).includes('analyzeResults/abc'), 'Azure: Ergebnisadresse aus Header');
ok(ev(wf7, 'If4', ['conditions', 'conditions', 0, 'leftValue'], {}, { operation_url: 'https://evil.example.com/x' }) === false, 'Azure: fremde Ergebnisadresse wird abgelehnt');
const fin3 = ev(wf7, 'Edit Fields7', ['jsonOutput'], { 'Edit Fields': [[[sel]]], 'Edit Fields2': [[[{ renderer_fehler: 'Renderer-Fehler: 500' }]]] }, { abschnitte: [{ fundstelle: 'Seite 1', text: 'A' }], extraktion: 'n8n' });
ok(/Renderer-Fehler: 500 – Ersatzweg genutzt/.test(fin3.hinweis) && fin3.abschnitte_anzahl === 1, 'Renderer-Ausfall wird im Ergebnis vermerkt');
ok(ev(wf7, 'HTTP Request1', ['headerParameters', 'parameters', 0, 'value'], {}, { endung: 'pptx' }).includes('presentationml'), 'Azure: Content-Type je Dateityp');

// ---------------------------------------------------------------- WF8
console.log('WF8 PPTX ohne Renderer');
const wf8 = load('08_ECOMEX_PPTX_ohne_Renderer_Claude.json');
const sample = JSON.parse(fs.readFileSync(path.join(ROOT, 'renderer/tests/sample_deck.json'), 'utf8'));
const auf = ev(wf8, 'Edit Fields', ['jsonOutput'], {}, { deck: sample, konfig: { claude_master_file_id: 'file_MASTER1', anthropic_version: '2026-10-21', code_execution_tool: 'code_execution_20260521', claude_pptx_modell: 'claude-sonnet-5-5' }, katalog: kat, design_regeln: '# Design' });
ok(auf.anthropic_request.messages[0].content.length === 2 && auf.anthropic_request.messages[0].content[1].file_id === 'file_MASTER1', 'Master wird als container_upload mitgegeben');
ok(auf.anthropic_request.container.skills[0].skill_id === 'pptx' && auf.anthropic_request.tools[0].type === 'code_execution_20260521', 'PPTX-Skill + Code-Execution gesetzt');
ok(/ECOMEX_ENTWURF/.test(auf.anthropic_request.messages[0].content[0].text) && /ECOMEX_M02_Tag12_ENTWURF/.test(auf.anthropic_request.messages[0].content[0].text), 'Auftrag enthält ENTWURF-Formname + Dateiname');
const resp1 = { stop_reason: 'pause_turn', container: { id: 'cont_1' }, content: [{ type: 'text', text: 'arbeite' }] };
const cont = ev(wf8, 'Edit Fields1', ['jsonOutput'], { 'Edit Fields': [[[auf]]] }, resp1);
ok(cont.runde === 2 && cont.anthropic_request.container.id === 'cont_1' && cont.anthropic_request.messages.length === 2, 'Pause → Fortsetzung im selben Container, Runde 2');
const resp2 = { stop_reason: 'pause_turn', container: { id: 'cont_1' }, content: [{ type: 'text', text: 'weiter' }] };
const cont2 = ev(wf8, 'Edit Fields1', ['jsonOutput'], { 'Edit Fields': [[[auf]]], 'Edit Fields1': [[[cont]]] }, resp2);
ok(cont2.runde === 3 && cont2.anthropic_request.messages.length === 2 && cont2.anthropic_request.messages[1].content.length === 2, 'zweite Pause: Assistent-Inhalt wird angehängt, nicht dupliziert');
ok(ev(wf8, 'If', ['conditions', 'conditions', 1, 'leftValue'], { 'Edit Fields1': [[[{ runde: 8 }]]] }, resp2) === 8, 'Rundenzähler für die 8-Runden-Grenze');
const r0 = { stop_reason: 'pause_turn', content: [{ type: 'bash_code_execution_tool_result', content: { type: 'bash_code_execution_result', content: [{ type: 'bash_code_execution_output', file_id: 'file_ALT' }] } }] };
const r1 = { stop_reason: 'end_turn', content: [{ type: 'bash_code_execution_tool_result', content: { content: [{ file_id: 'file_PPTX' }, { file_id: 'file_MASTER1' }] } }, { type: 'text', text: 'fertig' }] };
const fids = ev(wf8, 'Edit Fields2', ['jsonOutput'], { 'Edit Fields': [[[auf]]], 'Edit Fields1': [[[{ ...cont, runde: 2 }]]], 'HTTP Request': [[[r0]], [[r1]]] }, r1);
ok(JSON.stringify(fids.file_ids) === JSON.stringify(['file_PPTX', 'file_ALT']), 'Datei-IDs aus allen Runden, neueste zuerst, Master ausgeschlossen: ' + fids.file_ids.join(','));

// ---------------------------------------------------------------- WF2
console.log('WF2 Tag produzieren');
const wf2 = load('02_ECOMEX_Tag_produzieren.json');
const deck = { meta: { modul: 'M02', tag: 'Tag 12', thema: 'Testen', run_id: 'R1', erstellt_am: 'x', dateiname: 'ECOMEX_M02_Tag 12_ENTWURF', regel_versionen: [{ datei: 'design.md', sha: 'abc' }], katalog_version: '4' }, folien: sample.folien };
const ef1 = { deck, bloecke: [{ block: 1, titel: 'A', folien: 5, qa: { status: 'OK', befunde: [] }, quellen: [] }], konfig: { renderer_aktiv: false, renderer_status: 'Renderer nicht erreichbar', katalog_warnung: '' } };
let ber = ev(wf2, 'Edit Fields2', assignVal(wf2, 'Edit Fields2', 'bericht'), { 'Edit Fields1': [[[ef1]]], 'No Operation, do nothing': [[[{ json: { pptx_quelle: 'claude', master_verwendet: true, hinweis: 'PPTX von Claude' }, binary: { pptx: { fileName: 'x.pptx' } } }]]] }, {});
ok(/Claude-PPTX-Skill ohne Renderer \(mit ECOMEX-Master\)/.test(ber) && /Nicht durchgeführt \(ohne Renderer\)/.test(ber), 'QA-Bericht Claude-Weg');
ber = ev(wf2, 'Edit Fields2', assignVal(wf2, 'Edit Fields2', 'bericht'), { 'Edit Fields1': [[[ef1]]], 'No Operation, do nothing': [[[{ json: { pptx_quelle: 'keine', hinweis: 'Claude-API-Fehler: 529' } }]]] }, {});
ok(/KEINE PPTX/.test(ber) && /529/.test(ber), 'QA-Bericht ohne PPTX nennt den Grund');
const rep = { folien: 24, warnungen_anzahl: 1, kritisch: 0, demo_master: false, warnungen: [{ folie: 7, art: 'textueberlauf', text: 'zu lang' }] };
ber = ev(wf2, 'Edit Fields2', assignVal(wf2, 'Edit Fields2', 'bericht'), { 'Edit Fields1': [[[ef1]]], 'HTTP Request': [[[rep]]], Merge2: [[[{}]]], 'Analyze document': [[[{ content: [{ type: 'text', text: 'Folie 7: eng' }] }]]], 'No Operation, do nothing': [[[{ json: { content: [] }, binary: { pptx: {}, pdf: {} } }]]] }, {});
ok(/im ECOMEX-Originalmaster/.test(ber) && /Folie 7: eng/.test(ber) && /Folie 7 · textueberlauf/.test(ber), 'QA-Bericht Renderer-Weg mit visueller + Layoutprüfung');
const man = ev(wf2, 'Edit Fields4', ['jsonOutput'], {}, { deck });
ok(/<section>/.test(man.html) && man.dateiname.endsWith('_Manuskript.html') && (man.html.match(/<section>/g) || []).length === deck.folien.length, 'Manuskript: eine Sektion je Folie');
const ca = ev(wf2, 'Edit Fields5', ['jsonOutput'], { 'Edit Fields1': [[[ef1]]], 'Edit Fields': [[[{ regeln: { 'design.md': '# D' }, katalog: kat }]]] }, { error: { message: 'ECONNREFUSED' } });
ok(ca.design_regeln === '# D' && ca.katalog.layouts.length > 0 && /ECONNREFUSED/.test(ca.renderer_fehler), 'Auftrag für Claude-Weg inkl. Renderer-Fehler');

// ---------------------------------------------------------------- WF3
console.log('WF3 Wissensbasis-Filter');
const wf3 = load('03_ECOMEX_Block_produzieren_AGENTEN.json');
const fpath = ['options', 'metadata', 'metadataValues', 0, 'value'];
ok(ev(wf3, 'Supabase Vector Store', fpath, {}, { konfig: { wissensbasis_referenzen: true } }) === 'true', 'allow_reference = "true" (Referenzquellen werden gefunden)');
ok(ev(wf3, 'Supabase Vector Store', fpath, {}, { konfig: { wissensbasis_referenzen: false } }) === 'false', 'abschaltbar → nur approved');

// ---------------------------------------------------------------- WF5
console.log('WF5 Wissensbasis befüllen');
const wf5 = load('05_ECOMEX_Wissensbasis_befuellen.json');
const q = { source_id: 'ECO-KB-1', titel: 'Leitfaden', dateiname: 'Leitfaden.pdf', link: '', review_status: 'reference', access_class: 'internal', sha256: 'ab', konfig: {} };
const t7 = { source_type: 'pdf', abschnitte: [{ fundstelle: 'Seite 1', text: 'A' }], abschnitte_anzahl: 1, zeichen: 1, extraktion: 'n8n', hinweis: '' };
let e2 = ev(wf5, 'Edit Fields2', ['jsonOutput'], { Merge2: [[[q]]], Crypto: [[[{ sha256: 'ab12' }]]], "Call 'ECOMEX 7 | Text extrahieren'": [[[t7]]] }, { Key: 'ecomex-sources/Uploads/2026-11/ECO-KB-1_Leitfaden.pdf' });
ok(e2.sha256 === 'ab12' && e2.storage_provider === 'supabase_storage' && e2.storage_uri === 'supabase://ecomex-sources/Uploads/2026-11/ECO-KB-1_Leitfaden.pdf' && e2.abschnitte[0].locator === 'Seite 1', 'Upload ok → supabase_storage + URI, Abschnitte als content/locator');
e2 = ev(wf5, 'Edit Fields2', ['jsonOutput'], { Merge2: [[[{ ...q, link: 'https://ecomex.sharepoint.com/x' }]]], Crypto: [[[{ sha256: 'ab12' }]]], "Call 'ECOMEX 7 | Text extrahieren'": [[[t7]]] }, { error: 'upload failed' });
ok(e2.storage_provider === 'sharepoint' && /sharepoint/.test(e2.storage_uri), 'Upload fehlgeschlagen → Original-Link als Ablage');
const evs = ev(wf5, 'Edit Fields', assignVal(wf5, 'Edit Fields', 'access_class'), {}, { zugriff: 'restricted – vertraulich (Agenten nutzen es nicht)' });
ok(evs === 'restricted', 'Zugriffsklasse aus Formular → DB-Wert');
const up = ev(wf5, 'HTTP Request', ['url'], {}, { konfig: { supabase_url: 'https://x.supabase.co', supabase_bucket: 'ecomex-sources' }, source_id: 'ECO-KB-1', dateiname: 'Mein Leitfaden (final).pdf' });
ok(/^https:\/\/x\.supabase\.co\/storage\/v1\/object\/ecomex-sources\/Uploads\/\d{4}-\d{2}\/ECO-KB-1_Mein_Leitfaden_final_\.pdf$/.test(up), 'Upload-Pfad: ' + up);

// ---------------------------------------------------------------- WF10
console.log('WF10 Ablage einlesen');
const wf10 = load('10_ECOMEX_Ablage_einlesen.json');
const inv = [
  { object_path: 'Referenzdecks/KI Strategie/Bitkom.pdf', folder: 'Referenzdecks/KI Strategie', file_name: 'Bitkom.pdf', bytes: 1800000, empfohlen: true, grund: 'neu', storage_uri: 'supabase://ecomex-sources/Referenzdecks/KI Strategie/Bitkom.pdf', source_id_vorschlag: 'SB-1', source_type: 'pdf', updated_at: '2026-11-19T14:00:00Z' },
  { object_path: 'Referenzdecks/Coaching/KI_Coach.pptx', bytes: 201300706, empfohlen: true, grund: 'neu' },
  { object_path: 'Referenzdecks/Mastervorlage/ECOMEX_Masterlayout_6.2.pptx', bytes: 26844796, empfohlen: false, grund: 'Folienmaster – Vorlage, keine Wissensquelle' }];
const sett = { max_mb: 60, probelauf: false, review_status: 'reference', access_class: 'internal' };
const ausw = ev(wf10, 'Edit Fields1', ['jsonOutput'], { 'Edit Fields': [[[sett]]], 'HTTP Request': [[inv]] }, inv[0]);
ok(ausw.dateien.length === 1 && ausw.zu_gross.length === 1 && ausw.nicht_eingelesen.length === 1 && ausw.gesamt === 3, 'Auswahl: 1 einlesen, 1 zu groß, 1 ausgeschlossen');
const dl = ev(wf10, 'HTTP Request1', ['url'], { "Call 'ECOMEX 0 | Regelwerk & Katalog laden'": [[[{ konfig: { supabase_url: 'https://x.supabase.co', supabase_bucket: 'ecomex-sources' } }]]] }, inv[0]);
ok(dl === 'https://x.supabase.co/storage/v1/object/ecomex-sources/Referenzdecks/KI%20Strategie/Bitkom.pdf', 'Download-URL korrekt kodiert: ' + dl);
const datei = ev(wf10, 'Edit Fields3', ['jsonOutput'], { 'Loop Over Items': [[[], [inv[0]]]], 'Edit Fields': [[[sett]]] }, t7);
ok(datei.source_id === 'SB-1' && datei.neu === true && datei.titel === 'KI Strategie – Bitkom' && datei.modul === 'KI Strategie' && datei.abschnitte.length === 1, 'Quelle aus Ablage-Eintrag: ' + datei.titel);
const datei2 = ev(wf10, 'Edit Fields3', ['jsonOutput'], { 'Loop Over Items': [[[], [{ ...inv[0], registered_source_id: 'SB-ALT' }]]], 'Edit Fields': [[[sett]]] }, t7);
ok(datei2.source_id === 'SB-ALT' && datei2.neu === false, 'registriert ohne Text → vorhandene source_id, keine Neuanlage');
const brt = ev(wf10, 'Edit Fields7', ['jsonOutput'], { 'Edit Fields1': [[[ausw]]], 'Loop Over Items': [[[{ datei: 'Bitkom.pdf', status: 'eingelesen', chunks: 12, source_id: 'SB-1' }], []]], 'HTTP Request2': [[[{ review_status: 'reference', quellen: 1, quellen_ohne_text: 0, chunks: 12 }]]] }, {});
ok(brt.eingelesen === 1 && /Zu groß/.test(brt.bericht) && /reference: 1 Quellen, 12 Abschnitte/.test(brt.bericht), 'Bericht mit Ergebnis, Größenliste und DB-Stand');
const meta10 = wf10.nodes.find(n => n.name === 'Default Data Loader').parameters.options.metadata.metadataValues;
ok(meta10.some(m => m.name === 'embedding_model' && m.value === 'text-embedding-3-small') && meta10.every(m => !/Edit Fields2/.test(m.value)), 'Loader-Metadaten inkl. embedding_model, aus Edit Fields3');

console.log('WF11 Systemcheck');
const wf11 = load('11_ECOMEX_Systemcheck.json');
const C0 = "Call 'ECOMEX 0 | Regelwerk & Katalog laden'", C7 = "Call 'ECOMEX 7 | Text extrahieren'";
const okRun = { [C0]: [[[{ konfig: { renderer_aktiv: false, renderer_status: 'kein Renderer', azure_aktiv: true, katalog_quelle: 'GitHub' }, regelwerk_ok: true, regeln: { a: 1, b: 2 }, katalog: { layouts: new Array(24) } }]]],
  'HTTP Request': [[[{ review_status: 'reference', quellen: 3, chunks: 40 }]]], 'HTTP Request1': [[[{ data: [] }]]], 'HTTP Request2': [[[{ value: [] }]]],
  'HTTP Request3': [[[{ error: 'x' }]]], [C7]: [[[{ abschnitte_anzahl: 2, extraktion: 'n8n' }]]], 'Basic LLM Chain': [[[{ text: 'OK' }]]], 'Basic LLM Chain1': [[[{ text: 'OK' }]]], 'Supabase Vector Store': [[[{}]]] };
const sc = ev(wf11, 'Edit Fields3', ['jsonOutput'], okRun, {});
ok(sc.alles_bereit === true && /Alles bereit/.test(sc.bericht), 'Systemcheck: alles grün → „Alles bereit“');
const sc2 = ev(wf11, 'Edit Fields3', ['jsonOutput'], { ...okRun, 'HTTP Request': [[[{ error: { message: 'Could not find the function public.ecomex_kb_status' } }]]], 'Basic LLM Chain1': [[[{ pruefung: 'openai' }]]] }, {});
ok(sc2.offen === 2 && /003_content_factory_betrieb/.test(sc2.bericht) && /OpenAI/.test(sc2.bericht), 'Systemcheck: fehlende SQL-Funktion + OpenAI-Credential mit Handlungsanweisung');

console.log('Struktur: Dateien gehen nicht verloren');
const keeps = (wf, name) => { const n = wf.nodes.find(x => x.name === name); return n.parameters.includeOtherFields === true && !(n.parameters.options || {}).stripBinary; };
ok(keeps(load('01_ECOMEX_Neues_Kursdeck_START.json'), 'Edit Fields'), 'WF1 Edit Fields behält die hochgeladene Datei');
ok(keeps(wf5, 'Edit Fields'), 'WF5 Edit Fields behält die Datei');
ok(keeps(wf7, 'Edit Fields'), 'WF7 Edit Fields behält die Datei');
ok(keeps(wf8, 'Edit Fields3'), 'WF8 Edit Fields3 behält die PPTX');
ok(keeps(wf10, 'Edit Fields2'), 'WF10 Edit Fields2 behält die Datei');
ok((wf5.connections['Merge'].main[0] || []).some(c => c.node === 'Merge1' && c.index === 1) && !(wf5.connections['Crypto'].main[0] || []).some(c => c.node === 'Merge1'), 'WF5: Datei-Item kommt aus Merge, nicht aus Crypto');
const m1 = wf5.nodes.find(n => n.name === 'Merge1').parameters;
ok(m1.mode === 'chooseBranch' && m1.useDataOfInput === 2, 'WF5 Merge1 wartet auf beide Eingänge und gibt die Datei weiter');

console.log(fails ? ('\nFEHLER: ' + fails) : '\nAlle Tests bestanden.');
process.exit(fails ? 1 : 0);
