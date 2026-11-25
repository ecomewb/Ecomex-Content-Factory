# Neue bzw. umgebaute Workflows (v6): Renderer optional, Fallbacks ohne Renderer, Datenbank-Anbindung.
# Wird von build_workflows.py eingebunden (gleiche Hilfsfunktionen).


# =================================================================================================
# ECOMEX 0 | Konfiguration, Regelwerk & Katalog
# =================================================================================================
def build_wf0():
    w = WF(WF0)
    w.sticky("info", "## ECOMEX 0 · Konfiguration, Regelwerk & Katalog\nWird von allen anderen Workflows aufgerufen – nicht direkt starten.\n\n"
             "**Einziger Ort für Einstellungen:** Node **Edit Fields** (GitHub, Renderer-URL, Supabase, PPTX-Ersatz über Claude).\n\n"
             "1. **HTTP Request** prüft `/health` des Renderers. Nicht erreichbar → alle Workflows nehmen automatisch den Weg ohne Renderer.\n"
             "2. Aufrufe mit `nur_konfig: true` (Wissensbasis, Ablage, Freigabe) enden hier.\n"
             "3. Sonst: alle `.md`-Regeln aus `governance/` und den Layoutkatalog aus GitHub laden (Katalog notfalls vom Renderer).\n\n"
             "Credentials: GitHub in *List files*, *Get a file*, *Get a file1*; Header-Auth *ECOMEX Renderer* (`X-API-Key`) in *HTTP Request1*.",
             [-560, -160], 500, 560, 4)
    w.node(TRIG, "n8n-nodes-base.executeWorkflowTrigger", 1.1, {"inputSource": "passthrough"}, [0, 200])
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_params([
        assign("github_owner", "ecomewb"),
        assign("github_repo", "Ecomex-Content-Factory"),
        assign("branch", "main"),
        assign("regel_ordner", "governance"),
        assign("katalog_pfad", "renderer/app/catalog.json"),
        assign("renderer_url", "http://ecomex-renderer:8080"),
        assign("supabase_url", "https://bymgndzxyzepzuqnceyt.supabase.co"),
        assign("supabase_bucket", "ecomex-sources"),
        assign("wissensbasis_referenzen", True, "boolean"),
        assign("pptx_ohne_renderer", "claude"),
        assign("claude_pptx_modell", "claude-sonnet-5-5"),
        assign("claude_master_file_id", ""),
        assign("anthropic_version", "2026-10-21"),
        assign("code_execution_tool", "code_execution_20260521"),
    ]), [240, 200], "EINSTELLUNGEN (einziger Ort)")
    w.node("HTTP Request", "n8n-nodes-base.httpRequest", 4.2, {
        "method": "GET",
        "url": r"={{ String($json.renderer_url || '').trim() ? String($json.renderer_url).trim().replace(/\/+$/, '') + '/health' : 'http://renderer-nicht-konfiguriert.invalid/health' }}",
        "options": {"timeout": 8000, "response": {"response": {"fullResponse": True, "neverError": True}}}},
        [480, 200], "Renderer erreichbar?", onError="continueRegularOutput", alwaysOutputData=True)
    w.node("Edit Fields1", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const c = $('Edit Fields').first().json;
  const h = $json || {};
  const body = h.body && typeof h.body === 'object' ? h.body : {};
  const aktiv = Number(h.statusCode) === 200 && body.status === 'ok';
  const grund = h.error ? String(h.error.message || h.error.description || JSON.stringify(h.error)).slice(0, 160) : ('HTTP ' + (h.statusCode || '?'));
  const konfig = { ...c,
    renderer_url: String(c.renderer_url || '').trim().replace(/\/+$/, ''),
    supabase_url: String(c.supabase_url || '').trim().replace(/\/+$/, ''),
    renderer_aktiv: aktiv,
    renderer_status: aktiv ? ('Renderer erreichbar · Master: ' + body.master + (body.demo_master ? ' (DEMO – Originalmaster fehlt!)' : '')) : ('Renderer nicht erreichbar – Weg ohne Renderer (' + grund + ')'),
    renderer_master: body.master || '', renderer_demo_master: !!body.demo_master, renderer_katalog_version: body.katalog_version || '',
    geprueft_am: $now.toISO() };
  return { ...$('When Executed by Another Workflow').first().json, konfig };
})() }}"""), [720, 200], "Konfiguration + Renderer-Status")
    w.node("If", "n8n-nodes-base.if", 2.2, filter_params([
        cond("={{ $json.nur_konfig === true || $json.nur_konfig === 'true' }}", "boolean", "true", single=True)]),
        [960, 200], "nur Konfiguration gewünscht?")
    w.node("No Operation, do nothing", "n8n-nodes-base.noOp", 1, {}, [1200, 40], "Ergebnis: nur Konfiguration")
    w.node("List files", "n8n-nodes-base.github", 1.1, {
        "resource": "file", "operation": "list",
        "owner": rl_name("={{ $json.konfig.github_owner }}"), "repository": rl_name("={{ $json.konfig.github_repo }}"),
        "filePath": "={{ $json.konfig.regel_ordner }}"}, [1200, 300], "Regel-Ordner in GitHub auflisten")
    w.node("Filter", "n8n-nodes-base.filter", 2.2, filter_params([
        cond("={{ $json.type }}", "string", "equals", "file"),
        cond("={{ $json.name }}", "string", "endsWith", ".md")]), [1420, 300], "nur Markdown-Regeln",
        alwaysOutputData=True)
    gh = "$('Edit Fields1').first().json.konfig"
    w.node("Get a file", "n8n-nodes-base.github", 1.1, {
        "resource": "file", "operation": "get",
        "owner": rl_name("={{ " + gh + ".github_owner }}"), "repository": rl_name("={{ " + gh + ".github_repo }}"),
        "filePath": "={{ $json.path }}", "asBinaryProperty": False,
        "additionalParameters": {"reference": "={{ " + gh + ".branch }}"}},
        [1640, 300], "jede Regel LIVE laden", onError="continueRegularOutput")
    w.node("Edit Fields2", "n8n-nodes-base.set", 3.4, set_params([
        assign("datei", "={{ $json.name || '' }}"),
        assign("sha", "={{ $json.sha || '' }}"),
        assign("text", "={{ $json.content ? $json.content.base64Decode() : '' }}"),
    ]), [1860, 300], "Base64 → Text")
    w.node("Aggregate", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateAllItemData",
                                                        "destinationFieldName": "regeldateien", "options": {}},
           [2080, 300], "alle Regeln bündeln")
    w.node("Get a file1", "n8n-nodes-base.github", 1.1, {
        "resource": "file", "operation": "get",
        "owner": rl_name("={{ " + gh + ".github_owner }}"), "repository": rl_name("={{ " + gh + ".github_repo }}"),
        "filePath": "={{ " + gh + ".katalog_pfad }}", "asBinaryProperty": False,
        "additionalParameters": {"reference": "={{ " + gh + ".branch }}"}},
        [2300, 300], "Layoutkatalog aus GitHub", onError="continueRegularOutput", alwaysOutputData=True)
    w.node("If1", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ !!$json.content }}", "boolean", "true", single=True)]),
           [2520, 300], "Katalog in GitHub gefunden?")
    http_renderer(w, "HTTP Request1", "/katalog", [2740, 420], "Ersatz: Katalog vom Renderer", method="GET",
                  base="$('Edit Fields1').first().json.konfig.renderer_url", timeout=30000)
    w.nodes[-1]["onError"] = "continueRegularOutput"
    w.node("Edit Fields3", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const basis = $('Edit Fields1').first().json;
  const konfig = { ...basis.konfig };
  const dateien = ($('Aggregate').first().json.regeldateien || []).filter(r => r.datei);
  let kat = null, quelle = '';
  try { const g = $('Get a file1').first().json; if (g.content) { kat = JSON.parse(g.content.base64Decode()); quelle = 'GitHub ' + konfig.katalog_pfad; } } catch (e) { kat = null; }
  if (!kat && $('HTTP Request1').isExecuted && Array.isArray($('HTTP Request1').first().json.layouts)) { kat = $('HTTP Request1').first().json; quelle = 'Renderer /katalog'; }
  kat = kat || { layouts: [] };
  konfig.katalog_quelle = quelle || 'nicht gefunden';
  konfig.katalog_warnung = konfig.renderer_aktiv && konfig.renderer_katalog_version && kat.version && String(konfig.renderer_katalog_version) !== String(kat.version)
    ? ('Katalog im Renderer (v' + konfig.renderer_katalog_version + ') weicht von GitHub (v' + kat.version + ') ab – Renderer neu bauen.') : '';
  return { ...basis, konfig,
    regeln: Object.fromEntries(dateien.map(r => [r.datei, r.text])),
    regel_versionen: dateien.map(r => ({ datei: r.datei, sha: String(r.sha).slice(0, 7) })),
    katalog: { version: kat.version, regeln_fuer_agenten: kat.regeln_fuer_agenten || [], layouts: kat.layouts || [] },
    regelwerk_geladen_am: $now.toISO() };
})() }}"""), [2960, 300], "Regelwerk + Katalog + Konfiguration")
    w.node("If2", "n8n-nodes-base.if", 2.2, filter_params([
        cond("={{ ['curriculum.md','didaktik.md','design.md','qa_rules.md','content_workflow.md'].every(d => String(($json.regeln || {})[d] || '').length > 200) }}",
             "boolean", "true", single=True),
        cond("={{ ($json.katalog.layouts || []).length }}", "number", "gte", 10)]), [3180, 300],
        "Pflichtregeln + Katalog vollständig?")
    w.node("No Operation, do nothing1", "n8n-nodes-base.noOp", 1, {}, [3420, 200], "Ergebnis an Aufrufer")
    w.node("Stop and Error", "n8n-nodes-base.stopAndError", 1, {
        "errorMessage": "={{ 'Regelwerk unvollständig. Fehlend/zu kurz: ' + ['curriculum.md','didaktik.md','design.md','qa_rules.md','content_workflow.md'].filter(d => String(($json.regeln || {})[d] || '').length <= 200).join(', ') + ' | Gefunden in ' + $json.konfig.regel_ordner + ': ' + Object.keys($json.regeln || {}).join(', ') + ' | Katalog: ' + $json.konfig.katalog_quelle + ', ' + ($json.katalog.layouts || []).length + ' Layouts' }}"},
        [3420, 420], "sichtbarer Abbruch")
    w.chain(TRIG, "Edit Fields", "HTTP Request", "Edit Fields1", "If")
    w.link("If", "No Operation, do nothing", 0)
    w.link("If", "List files", 1)
    w.chain("List files", "Filter", "Get a file", "Edit Fields2", "Aggregate", "Get a file1", "If1")
    w.link("If1", "Edit Fields3", 0)
    w.link("If1", "HTTP Request1", 1)
    w.link("HTTP Request1", "Edit Fields3")
    w.link("Edit Fields3", "If2")
    w.link("If2", "No Operation, do nothing1", 0)
    w.link("If2", "Stop and Error", 1)
    w.save(OUT / "00_ECOMEX_Regelwerk_und_Katalog_laden.json")


# =================================================================================================
# ECOMEX 2 | Tag produzieren
# =================================================================================================
QA_BERICHT = r"""={{ (() => {
  const d = $('Edit Fields1').first().json;
  const m = d.deck.meta;
  const k = d.konfig || {};
  const out = $('No Operation, do nothing').first();
  const oj = out.json || {};
  const hatPptx = !!(out.binary && out.binary.pptx);
  const mitRenderer = $('Merge2').isExecuted;
  const r = $('HTTP Request').isExecuted && Array.isArray($('HTTP Request').first().json.warnungen) ? $('HTTP Request').first().json : null;
  const vis = $('Analyze document').isExecuted
    ? ((($('Analyze document').first().json.content || []).filter(c => c.type === 'text').map(c => c.text).join('\n')) || ('Visuelle Prüfung nicht verfügbar: ' + JSON.stringify($('Analyze document').first().json.error || 'keine Antwort').slice(0, 200)))
    : 'Keine visuelle KI-Prüfung (ohne Renderer gibt es keine PDF-Vorschau). Bitte alle Folien in PowerPoint sichten.';
  const L = [];
  L.push('# QA-Bericht · ' + m.modul + ' · ' + m.tag + ' · ' + m.thema);
  L.push('**Status: ENTWURF – menschliche Prüfung erforderlich.** Nichts davon ist eine Unterrichtsfreigabe.');
  L.push('');
  L.push('- Run-ID: ' + m.run_id + ' · erstellt: ' + m.erstellt_am);
  L.push('- Folien: ' + d.deck.folien.length);
  L.push('- PowerPoint: ' + (mitRenderer && hatPptx ? ('Renderer' + (r && r.demo_master ? ' – ACHTUNG: DEMO-Master, Originalmaster fehlt im Renderer' : ' im ECOMEX-Originalmaster')) : (hatPptx ? ('Claude-PPTX-Skill ohne Renderer' + (oj.master_verwendet ? ' (mit ECOMEX-Master)' : ' (OHNE Master – Design nachbearbeiten)')) : 'KEINE PPTX erzeugt')));
  if (!hatPptx || !mitRenderer) L.push('- Hinweis: ' + (oj.hinweis || k.renderer_status || ''));
  if (k.katalog_warnung) L.push('- WARNUNG: ' + k.katalog_warnung);
  L.push('- Regelwerk (GitHub-SHA): ' + (m.regel_versionen || []).map(v => v.datei + '@' + v.sha).join(', '));
  L.push('- Layoutkatalog: v' + m.katalog_version);
  L.push('');
  L.push('## 1. Übersicht je Block');
  L.push('| Block | Titel | Folien | QA | offene Befunde |');
  L.push('|---|---|---|---|---|');
  d.bloecke.forEach(b => L.push('| ' + b.block + ' | ' + b.titel + ' | ' + b.folien + ' | ' + b.qa.status + ' | ' + ((b.qa.nicht_behoben || []).length + (b.qa.status === 'OK' ? (b.qa.befunde || []).length : 0)) + ' |'));
  L.push('');
  L.push('## 2. Visuelle Prüfung (KI)');
  L.push(vis);
  L.push('');
  if (r) {
    L.push('## 3. Automatische Layoutprüfung (Renderer) – ' + r.warnungen_anzahl + ' Hinweise, davon kritisch: ' + r.kritisch);
    (r.warnungen || []).forEach(w => L.push('- Folie ' + w.folie + ' · ' + w.art + ': ' + w.text));
    if (r.hinweis_schrift) L.push('- ' + r.hinweis_schrift);
  } else {
    L.push('## 3. Automatische Layoutprüfung');
    L.push('- Nicht durchgeführt (ohne Renderer). Besonders prüfen: Textüberläufe, Platzhalter, Übungen mit Lösung.');
  }
  L.push('');
  L.push('## 4. Fachlich-didaktische QA je Block');
  d.bloecke.forEach(b => {
    L.push('### Block ' + b.block + ': ' + b.titel + ' (' + b.qa.status + ')');
    if (b.fehler) L.push('- FEHLER: ' + b.fehler);
    (b.qa.befunde || []).forEach(f => L.push('- [' + f.schwere + '] Folie ' + f.folie + (f.kategorie ? ' · ' + f.kategorie : '') + ': ' + f.befund + ' → ' + f.korrektur + (b.qa.status === 'UEBERARBEITET' ? ' _(Revision durchgeführt)_' : '')));
    (b.qa.nicht_behoben || []).forEach(x => L.push('- NICHT BEHOBEN: ' + x));
    (b.qa.offene_punkte || []).forEach(x => L.push('- OFFEN: ' + x));
  });
  L.push('');
  L.push('## 5. Quellen je Block');
  d.bloecke.forEach(b => { if ((b.quellen || []).length) { L.push('**Block ' + b.block + '**'); b.quellen.forEach(q => L.push('- ' + (q.titel || '') + (q.url ? ' – ' + q.url : '') + (q.datum ? ' (' + q.datum + ')' : '') + (q.art ? ' [' + q.art + ']' : ''))); } });
  L.push('');
  L.push('## 6. Checkliste für die Freigabe');
  ['Kernaussagen und Zahlen gegen Quellen geprüft', 'Werkzeugfunktionen/Klickpfade am aktuellen Stand getestet', 'Übungen einmal selbst durchgespielt (Material + Musterlösung)', 'Storyboard-Treue: Reihenfolge, Zeiten, Lernziele', 'Bild- und Screenshot-Platzhalter ersetzt', 'Folien in PowerPoint gesichtet (Überläufe, Master, Logo)', 'Dozent:in hat Sprechernotizen gelesen', 'Freigabe über „ECOMEX 6 | Freigabe & Ablage“'].forEach(x => L.push('- [ ] ' + x));
  return L.join('\n');
})() }}"""

MANUSKRIPT = r"""={{ (() => {
  const d = $json.deck;
  const e = s => String(s == null ? '' : s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c]);
  const val = v => Array.isArray(v) ? ('<ul>' + v.map(x => '<li>' + val(x) + '</li>').join('') + '</ul>')
    : (v && typeof v === 'object') ? ('<dl>' + Object.entries(v).map(([a, b]) => '<dt>' + e(a) + '</dt><dd>' + val(b) + '</dd>').join('') + '</dl>') : e(v);
  let h = '<!doctype html><html lang="de"><head><meta charset="utf-8"><title>' + e(d.meta.dateiname) + ' – Manuskript</title>'
    + '<style>body{font-family:Arial,sans-serif;max-width:920px;margin:2em auto;color:#1E3F63;line-height:1.45} section{border-top:3px solid #48AFE3;padding:.8em 0} '
    + 'h2{margin:.2em 0} small{color:#5E5F5E} dt{font-weight:bold;margin-top:.4em} .notiz{background:#F3F6FA;padding:.6em;white-space:pre-wrap} .pruefen{color:#B8431F}</style></head><body>';
  h += '<h1>' + e(d.meta.thema) + '</h1><p>' + e([d.meta.modul, d.meta.tag].filter(Boolean).join(' · ')) + ' · ENTWURF · ' + d.folien.length + ' Folien</p>';
  d.folien.forEach((f, i) => {
    const felder = { ...(f.felder || {}) };
    const titel = felder.titel; delete felder.titel;
    h += '<section><h2>Folie ' + (i + 1) + (titel ? ' · ' + e(titel) : '') + '</h2><small>Layout: ' + e(f.layout) + (f.block ? ' · ' + e(f.block) : '') + '</small>' + val(felder);
    if (f.notizen) h += '<p><b>Sprechernotiz</b></p><div class="notiz">' + e(f.notizen) + '</div>';
    if ((f.review_hinweise || []).length) h += '<p class="pruefen"><b>Prüfen:</b> ' + f.review_hinweise.map(e).join(' · ') + '</p>';
    h += '</section>';
  });
  return { html: h + '</body></html>', dateiname: d.meta.dateiname + '_Manuskript.html' };
})() }}"""

CLAUDE_AUFTRAG = r"""={{ (() => {
  const d = $('Edit Fields1').first().json;
  const job = $('Edit Fields').first().json;
  return { deck: d.deck, konfig: d.konfig, design_regeln: String((job.regeln || {})['design.md'] || ''), katalog: job.katalog || {},
    renderer_fehler: $json.error ? String($json.error.message || JSON.stringify($json.error)).slice(0, 300) : '' };
})() }}"""


def build_wf2():
    w = WF(WF2)
    w.sticky("info", "## ECOMEX 2 · Tag produzieren\nWird von **ECOMEX 1** aufgerufen (ein Lauf pro Tag, parallel).\n\n"
             "1. Blöcke nacheinander durch **ECOMEX 3** (Agenten-Team).\n"
             "2. Tagesrahmen (Titel, Tagesablauf, Lernziele) kommt aus dem Storyboard.\n"
             "3. **Mit Renderer:** Prüfbericht, PPTX im Originalmaster, PDF-Vorschau, visuelle KI-Prüfung.\n"
             "   **Ohne Renderer** (oder wenn er ausfällt): PPTX über **ECOMEX 8** (Claude-PPTX-Skill) – abschaltbar in ECOMEX 0.\n"
             "4. Immer: QA-Bericht, Folien-Manuskript (HTML) und Deckdaten (für ECOMEX 4).\n\n"
             "Ergebnis: Dateien im **Merge**-Node (Download); optional SharePoint / E-Mail.",
             [-560, -120], 500, 540, 4)
    w.node(TRIG, "n8n-nodes-base.executeWorkflowTrigger", 1.1, {"inputSource": "passthrough"}, [0, 200])
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_params([
        assign("tagesuebersicht", "={{ $json.zeilen.map(z => 'Block ' + z.Block + ' (' + z.Von + '–' + z.Bis + ', ' + z.Art + '): ' + z.Titel + ' – Inhalte: ' + (z.Inhalte || '-')).join('\\n') }}"),
    ], include_other=True), [240, 200], "Tagesübersicht für alle Agenten")
    w.node("Split Out", "n8n-nodes-base.splitOut", 1, {"fieldToSplitOut": "zeilen", "include": "allOtherFields",
                                                       "options": {"destinationFieldName": "zeile"}}, [460, 200],
           "ein Item pro Block")
    call(w, WF3, [680, 200], "Block für Block (Multi-Agenten)", mode="each", onError="continueRegularOutput")
    w.node("Aggregate", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateAllItemData",
                                                        "destinationFieldName": "bloecke", "options": {}}, [900, 200])
    w.node("Edit Fields1", "n8n-nodes-base.set", 3.4, set_raw(DECK_ZUSAMMENSETZEN), [1120, 200], "Deck zusammensetzen")
    w.node("If", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.konfig.renderer_aktiv }}", "boolean", "true", single=True)]),
           [1340, 200], "Renderer verfügbar?")
    body = "={{ JSON.stringify($('Edit Fields1').first().json.deck) }}"
    base = "$('Edit Fields1').first().json.konfig.renderer_url"
    http_renderer(w, "HTTP Request", "/render?format=report", [1560, 60], "Prüfbericht (deterministisch)",
                  body_expr=body, base=base)
    w.nodes[-1]["onError"] = "continueErrorOutput"
    http_renderer(w, "HTTP Request1", "/render?format=pptx", [1780, 60], "PPTX im Originalmaster", body_expr=body,
                  file_out="pptx", base=base)
    w.nodes[-1]["onError"] = "continueErrorOutput"
    http_renderer(w, "HTTP Request2", "/render?format=pdf", [2000, -60], "PDF-Vorschau", body_expr=body,
                  file_out="pdf", base=base)
    w.nodes[-1]["onError"] = "continueRegularOutput"
    w.node("Merge1", "n8n-nodes-base.merge", 3.2, {"mode": "combine", "combineBy": "combineByPosition", "options": {}},
           [2220, 60], "PPTX + PDF zusammen")
    w.node("Analyze document", "@n8n/n8n-nodes-langchain.anthropic", 1, {
        "resource": "document", "operation": "analyze", "modelId": SONNET, "text": P.VISUAL_QA,
        "inputType": "binary", "binaryPropertyName": "pdf", "simplify": True, "options": {"maxTokens": 12000}},
        [2440, -60], "Visuelle QA (Claude sieht die Folien)", onError="continueRegularOutput", retryOnFail=True,
        maxTries=2, waitBetweenTries=10000)
    w.node("Merge2", "n8n-nodes-base.merge", 3.2, {"mode": "combine", "combineBy": "combineByPosition", "options": {}},
           [2660, 60], "Dateien + visuelle Prüfung")
    w.node("Edit Fields5", "n8n-nodes-base.set", 3.4, set_raw(CLAUDE_AUFTRAG), [1780, 380],
           "Auftrag für den Weg ohne Renderer")
    w.node("If1", "n8n-nodes-base.if", 2.2, filter_params([
        cond("={{ $json.konfig.pptx_ohne_renderer }}", "string", "equals", "claude")]), [2000, 380],
        "PPTX über Claude erlaubt?")
    call(w, WF8, [2220, 300], "PPTX mit Claude-PPTX-Skill", onError="continueRegularOutput", alwaysOutputData=True)
    w.node("Edit Fields6", "n8n-nodes-base.set", 3.4, set_params([
        assign("pptx_quelle", "keine"),
        assign("hinweis", "={{ 'Keine PPTX: Renderer nicht verfügbar und PPTX über Claude ist ausgeschaltet (ECOMEX 0 › pptx_ohne_renderer). Manuskript und Deckdaten liegen bei. ' + ($json.renderer_fehler || '') }}"),
    ]), [2220, 480], "ohne PPTX weiter")
    w.node("No Operation, do nothing", "n8n-nodes-base.noOp", 1, {}, [2880, 200], "PPTX-Ergebnis (beide Wege)")
    w.node("Edit Fields2", "n8n-nodes-base.set", 3.4, set_params([
        assign("dateiname", "={{ $('Edit Fields1').first().json.deck.meta.dateiname + '_QA-Bericht.md' }}"),
        assign("bericht", QA_BERICHT),
    ]), [3100, 200], "QA-Bericht (Markdown)")
    w.node("Convert to text file", "n8n-nodes-base.convertToFile", 1.1, {
        "operation": "toText", "sourceProperty": "bericht", "binaryPropertyName": "data",
        "options": {"fileName": "={{ $json.dateiname }}"}}, [3320, 200], "Bericht als Datei")
    w.node("Convert to JSON", "n8n-nodes-base.convertToFile", 1.1, {
        "operation": "toJson", "mode": "once", "binaryPropertyName": "data",
        "options": {"fileName": "={{ $('Edit Fields1').first().json.deck.meta.dateiname + '_Deckdaten.json' }}"}},
        [1340, 700], "Deckdaten (für Überarbeitung)")
    w.node("Edit Fields4", "n8n-nodes-base.set", 3.4, set_raw(MANUSKRIPT), [1340, 880], "Folien-Manuskript (HTML)")
    w.node("Convert to text file1", "n8n-nodes-base.convertToFile", 1.1, {
        "operation": "toText", "sourceProperty": "html", "binaryPropertyName": "data",
        "options": {"fileName": "={{ $json.dateiname }}"}}, [1560, 880], "Manuskript als Datei")
    w.node("Merge", "n8n-nodes-base.merge", 3.2, {"numberInputs": 4}, [3540, 560], "ERGEBNIS: Dateien zum Download")
    w.node("Upload file", "n8n-nodes-base.microsoftSharePoint", 2, {
        "resource": "file", "operation": "upload", "site": rl_list(""),
        "fileName": "={{ $binary[Object.keys($binary)[0]].fileName }}",
        "binaryPropertyName": "={{ Object.keys($binary)[0] }}"}, [3780, 560],
        "optional: SharePoint (nach IT-Freigabe aktivieren)", disabled=True, onError="continueRegularOutput")
    w.node("Send email", "n8n-nodes-base.emailSend", 2.1, {
        "fromEmail": "content-factory@ecomex.de", "toEmail": "redaktion@ecomex.de",
        "subject": "={{ 'ECOMEX Entwurf fertig: ' + $('Edit Fields1').first().json.deck.meta.modul + ' ' + $('Edit Fields1').first().json.deck.meta.tag }}",
        "emailFormat": "text",
        "text": "={{ 'Der Entwurf ist fertig (' + $('Edit Fields1').first().json.deck.folien.length + ' Folien).\\nDateien: n8n-Ausführung ' + $execution.id + ' (Node „Merge“) bzw. SharePoint.\\nDer QA-Bericht hängt an.' }}",
        "options": {"attachments": "data", "appendAttribution": False}}, [3540, 20],
        "optional: Benachrichtigung (SMTP aktivieren)", disabled=True)
    # Verbindungen
    w.chain(TRIG, "Edit Fields", "Split Out", f"Call '{WF3}'", "Aggregate", "Edit Fields1", "If")
    w.link("If", "HTTP Request", 0)
    w.link("If", "Edit Fields5", 1)
    w.link("HTTP Request", "HTTP Request1", 0)
    w.link("HTTP Request", "Edit Fields5", 1)
    w.link("HTTP Request1", "HTTP Request2", 0)
    w.link("HTTP Request1", "Merge1", 0, 0)
    w.link("HTTP Request1", "Edit Fields5", 1)
    w.link("HTTP Request2", "Merge1", 0, 1)
    w.link("Merge1", "Analyze document")
    w.link("Merge1", "Merge2", 0, 0)
    w.link("Analyze document", "Merge2", 0, 1)
    w.link("Merge2", "No Operation, do nothing")
    w.link("Edit Fields5", "If1")
    w.link("If1", f"Call '{WF8}'", 0)
    w.link("If1", "Edit Fields6", 1)
    w.link(f"Call '{WF8}'", "No Operation, do nothing")
    w.link("Edit Fields6", "No Operation, do nothing")
    w.chain("No Operation, do nothing", "Edit Fields2", "Convert to text file")
    w.link("No Operation, do nothing", "Merge", 0, 0)
    w.link("Convert to text file", "Merge", 0, 1)
    w.link("Edit Fields1", "Convert to JSON")
    w.link("Convert to JSON", "Merge", 0, 2)
    w.link("Edit Fields1", "Edit Fields4")
    w.link("Edit Fields4", "Convert to text file1")
    w.link("Convert to text file1", "Merge", 0, 3)
    w.link("Convert to text file", "Send email")
    w.link("Merge", "Upload file")
    w.sticky("r", "### Mit Renderer\nPrüfbericht → PPTX → PDF → visuelle Prüfung. Fällt der Renderer aus, geht es automatisch unten weiter.",
             [1540, -260], 1340, 150, 5)
    w.sticky("o", "### Ohne Renderer\nPPTX über ECOMEX 8 (Claude-PPTX-Skill, mit ECOMEX-Master wenn in ECOMEX 0 hinterlegt) – oder ohne PPTX, nur Manuskript.",
             [1760, 600], 700, 150, 6)
    w.save(OUT / "02_ECOMEX_Tag_produzieren.json")


# =================================================================================================
# ECOMEX 4 | Deck überarbeiten
# =================================================================================================
def build_wf4():
    w = WF("ECOMEX 4 | Deck überarbeiten")
    w.sticky("info", "## ECOMEX 4 · Deck überarbeiten\nPunktuelle Änderungen ohne Neuproduktion des ganzen Tages.\n\n"
             "**Deckdaten (.json)** aus einem Lauf von ECOMEX 2 hochladen und wählen:\n"
             "- **Block neu erzeugen** – das Agenten-Team arbeitet den Block mit deinen Hinweisen neu aus; der Rest bleibt.\n"
             "- **Nur neu rendern** – z. B. nach Änderungen in der JSON-Datei oder am Master.\n\n"
             "Mit Renderer: PPTX im Originalmaster. Ohne Renderer: PPTX über ECOMEX 8 (Claude).\n"
             "Antwort: ZIP mit neuer PPTX + neuen Deckdaten.", [-560, -80], 480, 440, 4)
    w.node("On form submission", "n8n-nodes-base.formTrigger", 2.6, {
        "authentication": "n8nUserAuth", "formTitle": "ECOMEX · Deck überarbeiten",
        "formDescription": "Deckdaten (.json) eines Laufs hochladen. Ergebnis bleibt ein ENTWURF. Handänderungen aus PowerPoint sind in den Deckdaten nicht enthalten.",
        "formFields": {"values": [
            form_field("Deckdaten (.json)", "deckdaten", "file", required=True, multipleFiles=False, acceptFileTypes=".json"),
            form_field("Aktion", "aktion", "radio", required=True, fieldOptions=options(
                "Block neu erzeugen", "Nur neu rendern")),
            form_field("Blocknummer (bei „Block neu erzeugen“)", "block", "number", placeholder="z. B. 3"),
            form_field("Hinweise für die Redaktion", "hinweise", "textarea",
                       placeholder="Was soll anders werden? z. B. Übung praxisnäher, Beispiel aus dem Vertrieb, kürzer …"),
            form_field("Freigabe externe KI", "freigabe", "checkbox", required=True, fieldOptions=options(
                "Die Verarbeitung mit externen KI-Diensten ist intern freigegeben.")),
        ]}, "responseMode": "onReceived",
        "options": {"path": "ecomex-deck-ueberarbeiten", "buttonLabel": "Starten", "appendAttribution": False}},
        [0, 200], "Einstieg")
    w.node("Extract from JSON", "n8n-nodes-base.extractFromFile", 1, {
        "operation": "fromJson", "binaryPropertyName": "deckdaten", "destinationKey": "daten", "options": {}},
        [220, 200])
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_params([
        assign("deck", "={{ $json.daten.deck || $json.daten }}", "object"),
        assign("aktion", "={{ $('On form submission').first().json.aktion }}"),
        assign("block", "={{ String($('On form submission').first().json.block || '').trim() }}"),
        assign("hinweise", "={{ $('On form submission').first().json.hinweise || '' }}"),
    ]), [440, 200], "Deck + Auftrag")
    call(w, WF0, [660, 200], "Regeln + Katalog + Konfiguration LIVE")
    w.node("If", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.aktion }}", "string", "startsWith", "Block")]),
           [880, 200], "Block neu erzeugen?")
    w.node("Edit Fields1", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const d = $json.deck; const m = d.meta || {};
  const zeilen = m.storyboard_zeilen || [];
  const zeile = zeilen.find(z => String(z.Block) === String($json.block));
  return {
    gefunden: !!zeile, zeile: zeile || {}, run_id: (m.run_id || 'ECX') + '-REV', modul: m.modul, tag: m.tag, thema: m.thema,
    zielgruppe: m.zielgruppe || 'Heterogene, berufserfahrene Erwachsene',
    tagesuebersicht: zeilen.map(z => 'Block ' + z.Block + ' (' + z.Von + '–' + z.Bis + ', ' + z.Art + '): ' + z.Titel).join('\n'),
    revision: { hinweise: $json.hinweise || 'Bitte fachlich und didaktisch verbessern.', bisherige_folien: (d.folien || []).filter(f => f.block === 'Block ' + $json.block) },
    regeln: $json.regeln, katalog: $json.katalog, konfig: $json.konfig
  };
})() }}"""), [1100, 80], "Blockauftrag mit Hinweisen")
    w.node("If1", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.gefunden }}", "boolean", "true", single=True)]),
           [1320, 80], "Block im Storyboard?")
    w.node("Stop and Error", "n8n-nodes-base.stopAndError", 1, {
        "errorMessage": "={{ 'Block ' + $('Edit Fields').first().json.block + ' ist in den Deckdaten nicht enthalten. Vorhanden: ' + (($('Edit Fields').first().json.deck.meta || {}).storyboard_zeilen || []).map(z => z.Block).join(', ') }}"},
        [1540, 200])
    call(w, WF3, [1540, 0], "Agenten-Team arbeitet den Block neu aus")
    w.node("Edit Fields2", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const src = $('If').first().json;
  const d = JSON.parse(JSON.stringify(src.deck));
  const label = 'Block ' + src.block;
  const idx = d.folien.findIndex(f => f.block === label);
  const rest = d.folien.filter(f => f.block !== label);
  const pos = idx < 0 ? rest.length : idx;
  d.folien = [...rest.slice(0, pos), ...($json.folien || []), ...rest.slice(pos)];
  d.meta.revisionen = [...(d.meta.revisionen || []), { block: src.block, am: $now.toISO(), hinweise: src.hinweise, qa_status: ($json.qa || {}).status }];
  d.meta.entwurf = true;
  return { deck: d, konfig: src.konfig, qa_block: $json.qa };
})() }}"""), [1760, 0], "neuen Block einsetzen")
    w.node("Edit Fields3", "n8n-nodes-base.set", 3.4, set_params([
        assign("deck", "={{ $json.deck }}", "object"),
        assign("konfig", "={{ $json.konfig }}", "object"),
    ]), [1100, 400], "Deck unverändert")
    w.node("If2", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.konfig.renderer_aktiv }}", "boolean", "true", single=True)]),
           [2000, 120], "Renderer verfügbar?")
    http_renderer(w, "HTTP Request", "/render?format=pptx", [2220, 20], "PPTX neu rendern",
                  body_expr="={{ JSON.stringify($json.deck) }}", file_out="pptx")
    w.nodes[-1]["onError"] = "continueErrorOutput"
    w.node("Edit Fields4", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const src = ($('Edit Fields2').isExecuted ? $('Edit Fields2') : $('Edit Fields3')).first().json;
  const basis = $("Call 'ECOMEX 0 | Regelwerk & Katalog laden'").first().json;
  return { deck: src.deck, konfig: src.konfig, design_regeln: String((basis.regeln || {})['design.md'] || ''), katalog: basis.katalog || {},
    renderer_fehler: $json.error ? String($json.error.message || JSON.stringify($json.error)).slice(0, 300) : '' };
})() }}"""), [2220, 240], "Auftrag für den Weg ohne Renderer")
    w.node("If3", "n8n-nodes-base.if", 2.2, filter_params([
        cond("={{ $json.konfig.pptx_ohne_renderer }}", "string", "equals", "claude")]), [2440, 240], "PPTX über Claude erlaubt?")
    call(w, WF8, [2660, 180], "PPTX mit Claude-PPTX-Skill", onError="continueRegularOutput", alwaysOutputData=True)
    w.node("Edit Fields5", "n8n-nodes-base.set", 3.4, set_params([
        assign("pptx_quelle", "keine"),
        assign("hinweis", "Keine PPTX: Renderer nicht verfügbar und PPTX über Claude ist ausgeschaltet."),
    ]), [2660, 340], "ohne PPTX weiter")
    w.node("No Operation, do nothing", "n8n-nodes-base.noOp", 1, {}, [2880, 120], "PPTX-Ergebnis (beide Wege)")
    w.node("Convert to JSON", "n8n-nodes-base.convertToFile", 1.1, {
        "operation": "toJson", "mode": "once", "binaryPropertyName": "deck",
        "options": {"fileName": "={{ ($json.deck.meta.dateiname || 'ECOMEX_Deck') + '_Deckdaten.json' }}"}},
        [2000, 520], "neue Deckdaten")
    w.node("Merge", "n8n-nodes-base.merge", 3.2, {"mode": "combine", "combineBy": "combineByPosition", "options": {}},
           [3100, 300])
    w.node("Compress file(s)", "n8n-nodes-base.compression", 1.1, {
        "operation": "compress", "binaryPropertyName": "={{ Object.keys($binary || {}).join(',') }}", "outputFormat": "zip",
        "fileName": "={{ $now.toFormat('yyyyLLdd-HHmm') + '_ECOMEX_Deck_ueberarbeitet.zip' }}", "binaryPropertyOutput": "data"},
        [3320, 300])
    w.node("Form", "n8n-nodes-base.form", 2.5, {
        "operation": "completion", "respondWith": "returnBinary", "inputDataFieldName": "data",
        "completionTitle": "Überarbeitung fertig",
        "completionMessage": "={{ $('No Operation, do nothing').first().binary && $('No Operation, do nothing').first().binary.pptx ? 'Das ZIP enthält die neue PPTX (ENTWURF) und die aktualisierten Deckdaten.' : ('Das ZIP enthält die aktualisierten Deckdaten, aber keine PPTX: ' + ($('No Operation, do nothing').first().json.hinweis || 'unbekannter Fehler')) }}",
        "options": {}}, [3540, 300])
    w.chain("On form submission", "Extract from JSON", "Edit Fields", f"Call '{WF0}'", "If")
    w.link("If", "Edit Fields1", 0)
    w.link("If", "Edit Fields3", 1)
    w.link("Edit Fields1", "If1")
    w.link("If1", f"Call '{WF3}'", 0)
    w.link("If1", "Stop and Error", 1)
    w.link(f"Call '{WF3}'", "Edit Fields2")
    for src in ("Edit Fields2", "Edit Fields3"):
        w.link(src, "If2")
        w.link(src, "Convert to JSON")
    w.link("If2", "HTTP Request", 0)
    w.link("If2", "Edit Fields4", 1)
    w.link("HTTP Request", "No Operation, do nothing", 0)
    w.link("HTTP Request", "Edit Fields4", 1)
    w.link("Edit Fields4", "If3")
    w.link("If3", f"Call '{WF8}'", 0)
    w.link("If3", "Edit Fields5", 1)
    w.link(f"Call '{WF8}'", "No Operation, do nothing")
    w.link("Edit Fields5", "No Operation, do nothing")
    w.link("No Operation, do nothing", "Merge", 0, 0)
    w.link("Convert to JSON", "Merge", 0, 1)
    w.chain("Merge", "Compress file(s)", "Form")
    w.save(OUT / "04_ECOMEX_Deck_ueberarbeiten.json")


# =================================================================================================
# ECOMEX 5 | Wissensbasis befüllen (Einzeldatei per Formular)
# =================================================================================================
LOADER_METADATA = [
    ("source_id", "={{ $('Edit Fields2').first().json.source_id }}"),
    ("title", "={{ $('Edit Fields2').first().json.titel }}"),
    ("locator", "={{ $json.locator }}"),
    ("source_uri", "={{ $('Edit Fields2').first().json.storage_uri }}"),
    ("version_label", "={{ $('Edit Fields2').first().json.version }}"),
    ("file_name", "={{ $('Edit Fields2').first().json.dateiname }}"),
    ("module_id", "={{ $('Edit Fields2').first().json.modul }}"),
    ("review_status", "={{ $('Edit Fields2').first().json.review_status }}"),
    ("access_class", "={{ $('Edit Fields2').first().json.access_class }}"),
    ("embedding_model", "text-embedding-3-small"),
]


def kb_nodes(w, x, y, meta, note_store="durchsuchbar speichern"):
    """Supabase Vector Store (insert) mit Loader, Splitter, Embeddings – gemeinsamer Baustein für ECOMEX 5 und 10."""
    w.node("Supabase Vector Store", "@n8n/n8n-nodes-langchain.vectorStoreSupabase", 1.3, {
        "mode": "insert", "tableName": {"__rl": True, "mode": "id", "value": "ecomex_documents"},
        "options": {"queryName": "ecomex_match_documents"}}, [x, y], note_store)
    w.node("Default Data Loader", "@n8n/n8n-nodes-langchain.documentDefaultDataLoader", 1.1, {
        "jsonMode": "expressionData", "jsonData": "={{ $json.content }}", "textSplittingMode": "custom",
        "options": {"metadata": {"metadataValues": [{"name": n, "value": v} for n, v in meta]}}}, [x + 20, y + 240])
    w.node("Recursive Character Text Splitter", "@n8n/n8n-nodes-langchain.textSplitterRecursiveCharacterTextSplitter", 1,
           {"chunkSize": 1800, "chunkOverlap": 200, "options": {}}, [x + 80, y + 440])
    w.node("Embeddings OpenAI", "@n8n/n8n-nodes-langchain.embeddingsOpenAi", 1.2,
           {"model": "text-embedding-3-small", "options": {}}, [x - 120, y + 240])
    w.ai("Embeddings OpenAI", "Supabase Vector Store", "ai_embedding")
    w.ai("Default Data Loader", "Supabase Vector Store", "ai_document")
    w.ai("Recursive Character Text Splitter", "Default Data Loader", "ai_textSplitter")


def build_wf5():
    w = WF("ECOMEX 5 | Wissensbasis befüllen")
    w.sticky("info", "## ECOMEX 5 · Wissensbasis befüllen (eine Datei)\nEine Fachquelle per Formular durchsuchbar machen. Für die ganze Supabase-Ablage: **ECOMEX 10**.\n\n"
             "1. Konfiguration aus ECOMEX 0 (Renderer da?).\n2. SHA-256 der Datei → schon vorhanden? Dann Stopp.\n"
             "3. Text mit Fundstellen über **ECOMEX 7** (Renderer oder n8n).\n4. Original in die Supabase-Ablage (`Uploads/`), Quelle in `ecomex_sources`, Abschnitte in `ecomex_documents`.\n\n"
             "Status *reference* = Agenten dürfen nutzen, ist aber keine fachliche Freigabe. *restricted* wird von den Agenten nie gefunden.\n"
             "Credentials: Supabase (in *Get many rows*, *HTTP Request*, *Create a row*, *Supabase Vector Store*), OpenAI (Embeddings).",
             [-560, -120], 500, 520, 4)
    w.node("On form submission", "n8n-nodes-base.formTrigger", 2.6, {
        "authentication": "n8nUserAuth", "formTitle": "ECOMEX · Fachquelle in die Wissensbasis",
        "formDescription": "Ohne Renderer lesbar: PDF, Excel, CSV, Markdown/Text. Mit Renderer zusätzlich PowerPoint und Word. Ein Import ist keine fachliche Freigabe.",
        "formFields": {"values": [
            form_field("Titel", "titel", required=True, placeholder="z. B. M02 Tag 11 – Prompt-Muster (Deck 2026-09)"),
            form_field("Version", "version", placeholder="z. B. 2026-11 / v1"),
            form_field("Modul / Kurs", "modul", placeholder="z. B. M02 oder KI-Strategie"),
            form_field("Original-Link", "link", placeholder="https://… SharePoint oder GitHub (optional)"),
            form_field("Status", "status", "radio", required=True, fieldOptions=options(
                "reference – Referenz (Agenten dürfen nutzen, keine Freigabe)", "approved – fachlich freigegeben")),
            form_field("Zugriffsklasse", "zugriff", "radio", required=True, fieldOptions=options(
                "internal – intern", "public – öffentlich", "restricted – vertraulich (Agenten nutzen es nicht)")),
            form_field("Lizenz / Nutzungsrechte", "lizenz", placeholder="z. B. ECOMEX intern / Bitkom, frei verfügbar / Verlagsbuch – nur sinngemäß"),
            form_field("Datei", "datei", "file", required=True, multipleFiles=False,
                       acceptFileTypes=".pdf,.pptx,.docx,.xlsx,.csv,.md,.txt"),
            form_field("Freigabe externe KI", "freigabe", "checkbox", required=True, fieldOptions=options(
                "Die Datei darf für Embeddings an OpenAI übermittelt werden.")),
        ]}, "responseMode": "onReceived",
        "options": {"path": "ecomex-wissensimport", "buttonLabel": "Importieren", "appendAttribution": False}},
        [0, 200], "Einstieg")
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_params([
        assign("nur_konfig", True, "boolean"),
        assign("source_id", "={{ 'ECO-KB-' + $now.toFormat('yyyyLLddHHmmss') + '-' + $execution.id }}"),
        assign("titel", "={{ $json.titel.trim() }}"),
        assign("version", "={{ $json.version || 'ohne Angabe' }}"),
        assign("modul", "={{ $json.modul || '' }}"),
        assign("link", "={{ $json.link || '' }}"),
        assign("review_status", "={{ String($json.status || '').startsWith('approved') ? 'approved' : 'reference' }}"),
        assign("access_class", "={{ String($json.zugriff || 'internal').split(' ')[0] }}"),
        assign("license_note", "={{ $json.lizenz || '' }}"),
        assign("dateiname", "={{ $binary.datei.fileName }}"),
    ], include_other=True), [220, 200], "Angaben zur Quelle (Datei bleibt erhalten)")
    call(w, WF0, [440, 80], "nur Konfiguration (Renderer da?)")
    w.node("Merge", "n8n-nodes-base.merge", 3.2, {"mode": "combine", "combineBy": "combineByPosition", "options": {}},
           [660, 200], "Konfiguration + Quelle + Datei")
    w.node("Crypto", "n8n-nodes-base.crypto", 2, {"action": "hash", "type": "SHA256", "binaryData": True,
                                                   "binaryPropertyName": "datei", "dataPropertyName": "sha256",
                                                   "encoding": "hex"}, [880, 200], "Prüfsumme der Datei")
    w.node("Get many rows", "n8n-nodes-base.supabase", 1, {
        "resource": "row", "operation": "getAll", "tableId": "ecomex_sources", "returnAll": False, "limit": 1,
        "filterType": "manual", "matchType": "allFilters",
        "filters": {"conditions": [{"keyName": "sha256", "condition": "eq", "keyValue": "={{ $json.sha256 }}"}]}},
        [1100, 200], "schon in der Wissensbasis?", alwaysOutputData=True)
    w.node("If", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ !!$json.source_id }}", "boolean", "true", single=True)]),
           [1320, 200], "Duplikat?")
    w.node("Form", "n8n-nodes-base.form", 2.5, {
        "operation": "completion", "respondWith": "text", "completionTitle": "Schon vorhanden",
        "completionMessage": "={{ 'Diese Datei ist bereits in der Wissensbasis: ' + $json.title + ' (' + $json.source_id + ', Status ' + $json.review_status + '). Nichts wurde doppelt angelegt.' }}",
        "options": {}}, [1540, 60])
    w.node("Merge1", "n8n-nodes-base.merge", 3.2, {"mode": "chooseBranch", "chooseBranchMode": "waitForAll",
                                                   "output": "specifiedInput", "useDataOfInput": 2},
           [1540, 300], "weiter mit Datei (Item vor Crypto – Crypto entfernt die Datei)")
    call(w, WF7, [1760, 300], "Datei → Text mit Fundstellen")
    w.node("If1", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ Number($json.abschnitte_anzahl) || 0 }}", "number", "gt", 0)]),
           [1980, 300], "Text gefunden?")
    w.node("Form1", "n8n-nodes-base.form", 2.5, {
        "operation": "completion", "respondWith": "text", "completionTitle": "Nicht importiert",
        "completionMessage": "={{ 'Aus der Datei konnte kein Text gelesen werden. ' + ($json.hinweis || '') }}",
        "options": {}}, [2200, 440])
    w.node("Merge2", "n8n-nodes-base.merge", 3.2, {"mode": "chooseBranch", "chooseBranchMode": "waitForAll",
                                                   "output": "specifiedInput", "useDataOfInput": 2},
           [2200, 200], "Datei für die Ablage")
    http_supabase(w, "HTTP Request", "POST",
                  "/storage/v1/object/{{ $json.konfig.supabase_bucket }}/Uploads/{{ $now.toFormat('yyyy-LL') }}/{{ $json.source_id }}_{{ $json.dateiname.replace(/[^A-Za-z0-9._-]+/g, '_') }}",
                  [2420, 200], "Original in die Supabase-Ablage", binary_in="datei", headers=[("x-upsert", "true")],
                  onError="continueRegularOutput")
    w.node("Edit Fields2", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const q = $('Merge2').first().json;
  const t = $("Call 'ECOMEX 7 | Text extrahieren'").first().json;
  const key = $json.Key || '';
  const link = q.link || '';
  return { ...q, sha256: $('Crypto').first().json.sha256, source_type: t.source_type,
    storage_provider: key ? 'supabase_storage' : (link ? (/sharepoint/i.test(link) ? 'sharepoint' : 'external_url') : 'other'),
    storage_uri: key ? ('supabase://' + key) : (link || ('upload://' + q.dateiname)),
    abschnitte: (t.abschnitte || []).map(a => ({ content: a.text, locator: a.fundstelle })),
    notiz: t.abschnitte_anzahl + ' Abschnitte, ' + t.zeichen + ' Zeichen, gelesen per ' + t.extraktion + '. ' + (t.hinweis || '') };
})() }}"""), [2640, 200], "Quelle vollständig")
    w.node("Create a row", "n8n-nodes-base.supabase", 1, {
        "resource": "row", "operation": "create", "tableId": "ecomex_sources", "dataToSend": "defineBelow",
        "fieldsUi": {"fieldValues": [
            {"fieldId": "source_id", "fieldValue": "={{ $json.source_id }}"},
            {"fieldId": "title", "fieldValue": "={{ $json.titel }}"},
            {"fieldId": "source_type", "fieldValue": "={{ $json.source_type }}"},
            {"fieldId": "storage_provider", "fieldValue": "={{ $json.storage_provider }}"},
            {"fieldId": "storage_uri", "fieldValue": "={{ $json.storage_uri }}"},
            {"fieldId": "module_id", "fieldValue": "={{ $json.modul || null }}"},
            {"fieldId": "review_status", "fieldValue": "={{ $json.review_status }}"},
            {"fieldId": "access_class", "fieldValue": "={{ $json.access_class }}"},
            {"fieldId": "version_label", "fieldValue": "={{ $json.version }}"},
            {"fieldId": "sha256", "fieldValue": "={{ $json.sha256 }}"},
            {"fieldId": "license_note", "fieldValue": "={{ $json.license_note || null }}"},
            {"fieldId": "notes", "fieldValue": "={{ $json.notiz }}"},
        ]}}, [2860, 200], "Quelle registrieren")
    w.node("Split Out", "n8n-nodes-base.splitOut", 1, {"fieldToSplitOut": "abschnitte", "include": "noOtherFields", "options": {}},
           [3080, 200], "ein Item pro Folie/Seite/Abschnitt")
    kb_nodes(w, 3320, 200, LOADER_METADATA)
    w.node("Aggregate", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateIndividualFields",
                                                        "fieldsToAggregate": {"fieldToAggregate": [{"fieldToAggregate": "pageContent"}]},
                                                        "options": {}}, [3560, 200])
    w.node("Form2", "n8n-nodes-base.form", 2.5, {
        "operation": "completion", "respondWith": "text", "completionTitle": "Import abgeschlossen",
        "completionMessage": "={{ $('Edit Fields2').first().json.abschnitte.length + ' Abschnitte (' + ($json.pageContent || []).length + ' Suchbausteine) aus „' + $('Edit Fields2').first().json.titel + '“ sind jetzt durchsuchbar (Quelle ' + $('Edit Fields2').first().json.source_id + ', Status ' + $('Edit Fields2').first().json.review_status + ', Ablage: ' + $('Edit Fields2').first().json.storage_uri + ').' }}",
        "options": {}}, [3780, 200])
    w.chain("On form submission", "Edit Fields", f"Call '{WF0}'")
    w.link(f"Call '{WF0}'", "Merge", 0, 0)
    w.link("Edit Fields", "Merge", 0, 1)
    w.chain("Merge", "Crypto", "Get many rows", "If")
    w.link("If", "Form", 0)
    w.link("If", "Merge1", 1, 0)
    w.link("Merge", "Merge1", 0, 1)
    w.chain("Merge1", f"Call '{WF7}'", "If1")
    w.link("If1", "Merge2", 0, 0)
    w.link("Merge1", "Merge2", 0, 1)
    w.link("If1", "Form1", 1)
    w.chain("Merge2", "HTTP Request", "Edit Fields2", "Create a row")
    w.link("Create a row", "Split Out")
    w.link("Split Out", "Supabase Vector Store")
    w.chain("Supabase Vector Store", "Aggregate", "Form2")
    w.save(OUT / "05_ECOMEX_Wissensbasis_befuellen.json")


# =================================================================================================
# ECOMEX 6 | Freigabe & Ablage
# =================================================================================================
def build_wf6():
    w = WF("ECOMEX 6 | Freigabe & Ablage")
    w.sticky("info", "## ECOMEX 6 · Freigabe & Ablage\nNach der menschlichen Prüfung (auch nach Bearbeitung in PowerPoint):\n\n"
             "- **Freigegeben + Renderer da** → ENTWURF-Kennzeichnung wird entfernt, Version und Prüfer:in in die Dateieigenschaften.\n"
             "- **Freigegeben, kein Renderer** → Datei kommt unverändert zurück; ENTWURF-Kennzeichnung bitte in PowerPoint löschen (Form „ECOMEX_ENTWURF“ bzw. Fußzeile).\n"
             "- **Überarbeitung nötig** → nichts wird veröffentlicht.\n\n"
             "SharePoint (*Upload file*) erst nach IT-Freigabe aktivieren.", [-560, -80], 500, 420, 4)
    w.node("On form submission", "n8n-nodes-base.formTrigger", 2.6, {
        "authentication": "n8nUserAuth", "formTitle": "ECOMEX · Freigabe & Ablage",
        "formDescription": "Nur geprüfte Decks freigeben. Die Freigabe wird in der Datei vermerkt.",
        "formFields": {"values": [
            form_field("Geprüfte PPTX", "deck", "file", required=True, multipleFiles=False, acceptFileTypes=".pptx"),
            form_field("Prüfer:in", "pruefer", required=True),
            form_field("Entscheidung", "entscheidung", "radio", required=True, fieldOptions=options(
                "Freigegeben – veröffentlichen", "Überarbeitung nötig – nicht veröffentlichen")),
            form_field("Version", "version", required=True, placeholder="z. B. v1_0"),
            form_field("Kommentar", "kommentar", "textarea"),
        ]}, "responseMode": "onReceived",
        "options": {"path": "ecomex-freigabe", "buttonLabel": "Absenden", "appendAttribution": False}},
        [0, 200], "Einstieg")
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_params([
        assign("nur_konfig", True, "boolean"),
    ], include_other=True), [220, 200], "nur Konfiguration anfordern")
    call(w, WF0, [440, 80], "Renderer da?")
    w.node("Merge", "n8n-nodes-base.merge", 3.2, {"mode": "combine", "combineBy": "combineByPosition", "options": {}},
           [660, 200], "Konfiguration + Datei")
    w.node("If", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.entscheidung }}", "string", "startsWith", "Freigegeben")]),
           [880, 200], "freigegeben?")
    w.node("If1", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.konfig.renderer_aktiv }}", "boolean", "true", single=True)]),
           [1100, 100], "Renderer verfügbar?")
    http_renderer(w, "HTTP Request", "/finalisieren?version={{ encodeURIComponent($json.version) }}&pruefer={{ encodeURIComponent($json.pruefer) }}",
                  [1320, 0], "ENTWURF entfernen, Version setzen", multipart="deck", file_out="data")
    w.nodes[-1]["onError"] = "continueErrorOutput"
    w.node("Upload file", "n8n-nodes-base.microsoftSharePoint", 2, {
        "resource": "file", "operation": "upload", "site": rl_list(""),
        "fileName": "={{ $binary.data.fileName }}", "binaryPropertyName": "data"}, [1560, -120],
        "optional: SharePoint (nach IT-Freigabe aktivieren)", disabled=True)
    w.node("Form", "n8n-nodes-base.form", 2.5, {
        "operation": "completion", "respondWith": "returnBinary", "inputDataFieldName": "data",
        "completionTitle": "Freigegeben",
        "completionMessage": "={{ 'Die freigegebene Fassung (' + $('On form submission').first().json.version + ', geprüft von ' + $('On form submission').first().json.pruefer + ') wird heruntergeladen – ohne ENTWURF-Kennzeichnung. Ist SharePoint aktiviert, liegt sie zusätzlich in der Bibliothek.' }}",
        "options": {}}, [1560, 40])
    w.node("Upload file1", "n8n-nodes-base.microsoftSharePoint", 2, {
        "resource": "file", "operation": "upload", "site": rl_list(""),
        "fileName": "={{ $binary.deck.fileName }}", "binaryPropertyName": "deck"}, [1320, 200],
        "optional: SharePoint (nach IT-Freigabe aktivieren)", disabled=True)
    w.node("Form1", "n8n-nodes-base.form", 2.5, {
        "operation": "completion", "respondWith": "returnBinary", "inputDataFieldName": "deck",
        "completionTitle": "Freigegeben (ohne Renderer)",
        "completionMessage": "={{ 'Die Fassung ' + $('On form submission').first().json.version + ' (geprüft von ' + $('On form submission').first().json.pruefer + ') ist als freigegeben vermerkt. Der Renderer war nicht erreichbar: Bitte die ENTWURF-Kennzeichnung in PowerPoint löschen und die Datei mit Version im Namen ablegen.' }}",
        "options": {}}, [1320, 340])
    w.node("Form2", "n8n-nodes-base.form", 2.5, {
        "operation": "completion", "respondWith": "text", "completionTitle": "Renderer-Fehler",
        "completionMessage": "={{ 'Die Freigabe konnte nicht verarbeitet werden: ' + String(($json.error && ($json.error.message || $json.error)) || 'unbekannt').slice(0, 300) + '. Bitte erneut versuchen oder die ENTWURF-Kennzeichnung in PowerPoint selbst löschen.' }}",
        "options": {}}, [1560, 200])
    w.node("Form3", "n8n-nodes-base.form", 2.5, {
        "operation": "completion", "respondWith": "text", "completionTitle": "Nicht veröffentlicht",
        "completionMessage": "Das Deck wurde nicht veröffentlicht. Überarbeitung z. B. mit „ECOMEX 4 | Deck überarbeiten“ oder direkt in PowerPoint.",
        "options": {}}, [1100, 480])
    w.chain("On form submission", "Edit Fields", f"Call '{WF0}'")
    w.link(f"Call '{WF0}'", "Merge", 0, 0)
    w.link("Edit Fields", "Merge", 0, 1)
    w.link("Merge", "If")
    w.link("If", "If1", 0)
    w.link("If", "Form3", 1)
    w.link("If1", "HTTP Request", 0)
    w.link("If1", "Upload file1", 1)
    w.link("If1", "Form1", 1)
    w.link("HTTP Request", "Upload file", 0)
    w.link("HTTP Request", "Form", 0)
    w.link("HTTP Request", "Form2", 1)
    w.save(OUT / "06_ECOMEX_Freigabe_und_Ablage.json")


# =================================================================================================
# ECOMEX 7 | Text extrahieren (Renderer oder n8n)
# =================================================================================================
TEXT_ABSCHLUSS = r"""={{ (() => {
  const s = $('Edit Fields').first().json;
  const ab = ($json.abschnitte || []).filter(a => a && String(a.text || '').trim()).map(a => ({ fundstelle: String(a.fundstelle || ''), text: String(a.text).trim() }));
  const text = ab.map(a => '[' + a.fundstelle + ']\n' + a.text).join('\n\n');
  const map = { pdf: 'pdf', pptx: 'pptx', docx: 'docx', md: 'md', txt: 'md' };
  return { dateiname: s.dateiname, typ: s.endung, source_type: map[s.endung] || 'other', abschnitte: ab, abschnitte_anzahl: ab.length,
    text, zeichen: text.length, extraktion: $json.extraktion || 'n8n',
    hinweis: $json.hinweis || (ab.length ? '' : 'Kein lesbarer Text gefunden (z. B. gescanntes PDF ohne Texterkennung).') };
})() }}"""


def build_wf7():
    w = WF(WF7)
    w.sticky("info", "## ECOMEX 7 · Text extrahieren\nWird von ECOMEX 1, 5 und 10 aufgerufen. Erwartet die Datei im Binärfeld **datei** und `konfig` aus ECOMEX 0.\n\n"
             "**Mit Renderer:** `/extract` – PPTX (Folie + Notizen), Word, Excel, PDF, Markdown mit Fundstellen.\n"
             "**Ohne Renderer:** n8n-eigene Bausteine – PDF (je Seite), Excel/CSV (je 25 Zeilen), Markdown/Text (je Abschnitt).\n"
             "PowerPoint und Word gehen ohne Renderer nicht → bitte als PDF speichern.\n\n"
             "Ergebnis immer gleich: `abschnitte[{fundstelle,text}]`, `text`, `zeichen`, `source_type`, `hinweis`.",
             [-560, -100], 500, 460, 4)
    w.node(TRIG, "n8n-nodes-base.executeWorkflowTrigger", 1.1, {"inputSource": "passthrough"}, [0, 300])
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_params([
        assign("dateiname", "={{ $json.dateiname || ($binary.datei && $binary.datei.fileName) || 'datei' }}"),
        assign("endung", "={{ String($json.dateiname || ($binary.datei && $binary.datei.fileName) || '').split('.').pop().toLowerCase() }}"),
        assign("renderer_aktiv", "={{ !!($json.konfig && $json.konfig.renderer_aktiv) }}", "boolean"),
        assign("konfig", "={{ $json.konfig || {} }}", "object"),
    ], include_other=True), [220, 300], "Dateityp + Weg bestimmen (Datei bleibt erhalten)")
    w.node("If", "n8n-nodes-base.if", 2.2, filter_params([
        cond("={{ $json.renderer_aktiv }}", "boolean", "true", single=True),
        cond("={{ ['pdf','pptx','docx','xlsx','md','txt','csv'].includes($json.endung) }}", "boolean", "true", single=True)]),
        [440, 300], "Renderer nutzen?")
    http_renderer(w, "HTTP Request", "/extract", [660, 140], "Renderer liest die Datei", multipart="datei", timeout=300000)
    w.nodes[-1]["onError"] = "continueErrorOutput"
    w.node("Edit Fields1", "n8n-nodes-base.set", 3.4, set_params([
        assign("abschnitte", "={{ $json.abschnitte || [] }}", "array"),
        assign("hinweis", "={{ $json.hinweis || '' }}"),
        assign("extraktion", "renderer"),
    ]), [880, 60], "Ergebnis (Renderer)")
    w.node("Edit Fields2", "n8n-nodes-base.set", 3.4, set_params([
        assign("abschnitte", "={{ [] }}", "array"),
        assign("hinweis", "={{ 'Renderer konnte die Datei nicht lesen: ' + String(($json.error && ($json.error.message || $json.error.description)) || $json.error || 'unbekannt').slice(0, 250) }}"),
        assign("extraktion", "renderer"),
    ]), [880, 220], "Renderer-Fehler")
    w.node("Switch", "n8n-nodes-base.switch", 3.2, {
        "rules": {"values": [
            {"conditions": filter_params([cond("={{ $json.endung }}", "string", "equals", "pdf")])["conditions"],
             "renameOutput": True, "outputKey": "PDF"},
            {"conditions": filter_params([cond("={{ ['xlsx','xls','ods'].includes($json.endung) }}", "boolean", "true", single=True)])["conditions"],
             "renameOutput": True, "outputKey": "Excel"},
            {"conditions": filter_params([cond("={{ $json.endung }}", "string", "equals", "csv")])["conditions"],
             "renameOutput": True, "outputKey": "CSV"},
            {"conditions": filter_params([cond("={{ ['md','txt','html','htm','json'].includes($json.endung) }}", "boolean", "true", single=True)])["conditions"],
             "renameOutput": True, "outputKey": "Text"},
        ]},
        "options": {"fallbackOutput": "extra", "renameFallbackOutput": "nicht lesbar"}}, [660, 520], "ohne Renderer: nach Dateityp")
    w.node("Extract from File", "n8n-nodes-base.extractFromFile", 1, {
        "operation": "pdf", "binaryPropertyName": "datei", "options": {"joinPages": False}}, [900, 380], "PDF je Seite",
        onError="continueRegularOutput")
    w.node("Edit Fields3", "n8n-nodes-base.set", 3.4, set_params([
        assign("abschnitte", "={{ (Array.isArray($json.text) ? $json.text : [String($json.text || '')]).map((t, i) => ({ fundstelle: 'Seite ' + (i + 1), text: String(t || '') })) }}", "array"),
        assign("hinweis", "={{ $json.error ? ('PDF nicht lesbar: ' + String($json.error.message || $json.error).slice(0, 200)) : '' }}"),
        assign("extraktion", "n8n"),
    ]), [1120, 380], "Seiten → Abschnitte")
    w.node("Extract from File1", "n8n-nodes-base.extractFromFile", 1, {
        "operation": "xlsx", "binaryPropertyName": "datei", "options": {}}, [900, 520], "Excel-Zeilen",
        onError="continueRegularOutput")
    w.node("Extract from File2", "n8n-nodes-base.extractFromFile", 1, {
        "operation": "csv", "binaryPropertyName": "datei", "options": {}}, [900, 660], "CSV-Zeilen",
        onError="continueRegularOutput")
    w.node("Aggregate", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateAllItemData",
                                                        "destinationFieldName": "zeilen", "options": {}}, [1120, 580])
    w.node("Edit Fields4", "n8n-nodes-base.set", 3.4, set_params([
        assign("abschnitte", r"""={{ (() => { const z = ($json.zeilen || []).filter(r => r && !r.error); const out = []; for (let i = 0; i < z.length; i += 25) { out.push({ fundstelle: 'Zeilen ' + (i + 2) + '–' + (Math.min(i + 25, z.length) + 1), text: z.slice(i, i + 25).map(r => Object.entries(r).filter(([k, v]) => v !== '' && v != null).map(([k, v]) => k + ': ' + v).join('; ')).join('\n') }); } return out; })() }}""", "array"),
        assign("extraktion", "n8n"),
    ]), [1340, 580], "Zeilen → Abschnitte")
    w.node("Extract from File3", "n8n-nodes-base.extractFromFile", 1, {
        "operation": "text", "binaryPropertyName": "datei", "destinationKey": "inhalt", "options": {}}, [900, 800],
        "Text/Markdown", onError="continueRegularOutput")
    w.node("Edit Fields5", "n8n-nodes-base.set", 3.4, set_params([
        assign("abschnitte", r"""={{ (() => { const t = String($json.inhalt || ''); const teile = t.split(/\n(?=#{1,3} )/); const out = []; let n = 0; teile.forEach(p => { for (let i = 0; i < p.length; i += 4000) { n += 1; const kopf = (p.match(/^#{1,3} (.+)/) || [])[1]; out.push({ fundstelle: kopf ? ('Abschnitt ' + n + ': ' + kopf.slice(0, 60)) : ('Abschnitt ' + n), text: p.slice(i, i + 4000) }); } }); return out; })() }}""", "array"),
        assign("extraktion", "n8n"),
    ]), [1120, 800], "Abschnitte bilden")
    w.node("Edit Fields6", "n8n-nodes-base.set", 3.4, set_params([
        assign("abschnitte", "={{ [] }}", "array"),
        assign("hinweis", "={{ 'Dateityp .' + $json.endung + ' kann ohne Renderer nicht gelesen werden. Bitte als PDF speichern und erneut hochladen.' }}"),
        assign("extraktion", "n8n"),
    ]), [900, 960], "nicht lesbar")
    w.node("Edit Fields7", "n8n-nodes-base.set", 3.4, set_raw(TEXT_ABSCHLUSS), [1580, 300], "einheitliches Ergebnis")
    w.node("No Operation, do nothing", "n8n-nodes-base.noOp", 1, {}, [1800, 300], "Ergebnis an Aufrufer")
    w.chain(TRIG, "Edit Fields", "If")
    w.link("If", "HTTP Request", 0)
    w.link("If", "Switch", 1)
    w.link("HTTP Request", "Edit Fields1", 0)
    w.link("HTTP Request", "Edit Fields2", 1)
    w.link("Switch", "Extract from File", 0)
    w.link("Switch", "Extract from File1", 1)
    w.link("Switch", "Extract from File2", 2)
    w.link("Switch", "Extract from File3", 3)
    w.link("Switch", "Edit Fields6", 4)
    w.link("Extract from File", "Edit Fields3")
    w.link("Extract from File1", "Aggregate")
    w.link("Extract from File2", "Aggregate")
    w.link("Aggregate", "Edit Fields4")
    w.link("Extract from File3", "Edit Fields5")
    for n in ("Edit Fields1", "Edit Fields2", "Edit Fields3", "Edit Fields4", "Edit Fields5", "Edit Fields6"):
        w.link(n, "Edit Fields7")
    w.link("Edit Fields7", "No Operation, do nothing")
    w.save(OUT / "07_ECOMEX_Text_extrahieren.json")


# =================================================================================================
# ECOMEX 8 | PPTX ohne Renderer (Claude-PPTX-Skill)
# =================================================================================================
def build_wf8():
    w = WF(WF8)
    w.sticky("info", "## ECOMEX 8 · PPTX ohne Renderer (Claude)\nErsatzweg, wenn der Renderer fehlt oder ausfällt. Aufgerufen von ECOMEX 2 und 4.\n\n"
             "Claude baut mit dem **PPTX-Skill** aus den Deckdaten eine PowerPoint – mit dem ECOMEX-Master, wenn in ECOMEX 0 eine "
             "`claude_master_file_id` steht (einmalig über **ECOMEX 9** hochladen).\n\n"
             "Ablauf: Auftrag → Claude arbeitet (bei Pausen automatisch fortsetzen, max. 8 Runden) → erzeugte Datei suchen → PPTX herunterladen.\n"
             "Langsamer und weniger exakt als der Renderer; das Ergebnis immer in PowerPoint sichten.\n\n"
             "Credential: Anthropic (dasselbe wie bei den Agenten) in allen **HTTP Request**-Nodes.",
             [-560, -120], 520, 480, 4)
    w.node(TRIG, "n8n-nodes-base.executeWorkflowTrigger", 1.1, {"inputSource": "passthrough"}, [0, 200])
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_raw(P.CLAUDE_PPTX_AUFTRAG), [220, 200], "Auftrag an Claude")
    http_anthropic(w, "HTTP Request", "POST", "https://api.anthropic.com/v1/messages", "={{ $json.anthropic_version }}",
                   [460, 200], "Claude arbeitet (PPTX-Skill)", json_body="={{ JSON.stringify($json.anthropic_request) }}",
                   retryOnFail=True, maxTries=3, waitBetweenTries=20000, onError="continueErrorOutput")
    w.node("If", "n8n-nodes-base.if", 2.2, filter_params([
        cond("={{ $json.stop_reason }}", "string", "equals", "pause_turn"),
        cond("={{ ($('Edit Fields1').isExecuted ? $('Edit Fields1').last().json.runde : 1) }}", "number", "lt", 8)]),
        [700, 200], "Claude hat pausiert?")
    w.node("Edit Fields1", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const prev = $('Edit Fields1').isExecuted ? $('Edit Fields1').last().json : $('Edit Fields').first().json;
  const req = JSON.parse(JSON.stringify(prev.anthropic_request));
  const msgs = req.messages;
  const last = msgs[msgs.length - 1];
  if (last && last.role === 'assistant') { last.content = (last.content || []).concat($json.content || []); }
  else { msgs.push({ role: 'assistant', content: $json.content || [] }); }
  req.container = { ...(req.container || {}), id: ($json.container && $json.container.id) || (req.container || {}).id };
  return { ...prev, anthropic_request: req, runde: (prev.runde || 1) + 1 };
})() }}"""), [940, 60], "fortsetzen (gleicher Container)")
    w.node("Edit Fields2", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const auftrag = $('Edit Fields').first().json;
  const runden = $('Edit Fields1').isExecuted ? $('Edit Fields1').last().json.runde : 1;
  let ids = [];
  for (let r = 0; r < runden; r++) {
    try {
      $('HTTP Request').all(0, r).forEach(it => {
        const s = JSON.stringify(it.json.content || []);
        (s.match(/"file_id":"file_[A-Za-z0-9_-]+"/g) || []).forEach(m => ids.push(m.slice(11, -1)));
      });
    } catch (e) { }
  }
  ids = [...new Set(ids)].filter(id => id !== auftrag.master_file_id).reverse();
  return { file_ids: ids, stop_reason: $json.stop_reason || '', runden, anthropic_version: auftrag.anthropic_version,
    master_verwendet: auftrag.master_verwendet, dateiname: auftrag.dateiname };
})() }}"""), [940, 340], "erzeugte Dateien finden")
    w.node("If1", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.file_ids.length }}", "number", "gt", 0)]),
           [1180, 340], "Dateien vorhanden?")
    w.node("Split Out", "n8n-nodes-base.splitOut", 1, {"fieldToSplitOut": "file_ids", "include": "allOtherFields",
                                                       "options": {"destinationFieldName": "file_id"}}, [1400, 260])
    http_anthropic(w, "HTTP Request1", "GET", "={{ 'https://api.anthropic.com/v1/files/' + $json.file_id }}",
                   "={{ $json.anthropic_version }}", [1620, 260], "Dateiname prüfen", timeout=60000,
                   onError="continueRegularOutput")
    w.node("Filter", "n8n-nodes-base.filter", 2.2, filter_params([
        cond("={{ String($json.filename || '').toLowerCase() }}", "string", "endsWith", ".pptx")]),
        [1840, 260], "nur PowerPoint", alwaysOutputData=True)
    w.node("Limit", "n8n-nodes-base.limit", 1, {"maxItems": 1}, [2060, 260], "neueste PPTX")
    http_anthropic(w, "HTTP Request2", "GET", "={{ 'https://api.anthropic.com/v1/files/' + $json.id + '/content' }}",
                   "={{ $('Edit Fields2').first().json.anthropic_version }}", [2280, 260], "PPTX herunterladen",
                   file_out="pptx", timeout=180000, onError="continueErrorOutput")
    w.node("Edit Fields3", "n8n-nodes-base.set", 3.4, set_params([
        assign("pptx_quelle", "claude"),
        assign("claude_runden", "={{ $('Edit Fields2').first().json.runden }}", "number"),
        assign("master_verwendet", "={{ $('Edit Fields2').first().json.master_verwendet }}", "boolean"),
        assign("hinweis", "={{ 'PPTX von Claude (PPTX-Skill, ' + $('Edit Fields2').first().json.runden + ' Runde(n), ' + ($('Edit Fields2').first().json.master_verwendet ? 'mit ECOMEX-Master' : 'ohne Master – Design nachbearbeiten') + '). Keine automatische Layoutprüfung.' }}"),
    ], include_other=True), [2500, 180], "Ergebnis: PPTX (Datei bleibt erhalten)")
    w.node("Edit Fields4", "n8n-nodes-base.set", 3.4, set_params([
        assign("pptx_quelle", "keine"),
        assign("hinweis", r"""={{ $json.error ? ('Claude-API-Fehler: ' + String($json.error.message || JSON.stringify($json.error)).slice(0, 300)) : ('Claude hat keine PowerPoint-Datei geliefert (stop_reason: ' + ($('Edit Fields2').isExecuted ? $('Edit Fields2').first().json.stop_reason : '?') + '). Ohne Renderer bitte Manuskript nutzen oder den Lauf wiederholen.') }}"""),
    ]), [2500, 440], "Ergebnis: keine PPTX")
    w.node("No Operation, do nothing", "n8n-nodes-base.noOp", 1, {}, [2740, 300], "Ergebnis an Aufrufer")
    w.chain(TRIG, "Edit Fields", "HTTP Request")
    w.link("HTTP Request", "If", 0)
    w.link("HTTP Request", "Edit Fields4", 1)
    w.link("If", "Edit Fields1", 0)
    w.link("If", "Edit Fields2", 1)
    w.link("Edit Fields1", "HTTP Request")
    w.link("Edit Fields2", "If1")
    w.link("If1", "Split Out", 0)
    w.link("If1", "Edit Fields4", 1)
    w.chain("Split Out", "HTTP Request1", "Filter", "Limit", "HTTP Request2")
    w.link("HTTP Request2", "Edit Fields3", 0)
    w.link("HTTP Request2", "Edit Fields4", 1)
    w.link("Edit Fields3", "No Operation, do nothing")
    w.link("Edit Fields4", "No Operation, do nothing")
    w.save(OUT / "08_ECOMEX_PPTX_ohne_Renderer_Claude.json")


# =================================================================================================
# ECOMEX 9 | Master an Claude übergeben (einmalig)
# =================================================================================================
def build_wf9():
    w = WF(WF9)
    w.sticky("info", "## ECOMEX 9 · Master an Claude übergeben (einmalig)\nNur nötig für den Weg **ohne Renderer** (ECOMEX 8).\n\n"
             "Lädt den ECOMEX-Folienmaster in die Anthropic Files API. Die angezeigte `file_id` in **ECOMEX 0 › Edit Fields › claude_master_file_id** eintragen.\n"
             "Bei einem neuen Master erneut ausführen.\n\nCredential: Anthropic in *HTTP Request*.", [-560, -80], 480, 360, 4)
    w.node("On form submission", "n8n-nodes-base.formTrigger", 2.6, {
        "authentication": "n8nUserAuth", "formTitle": "ECOMEX · Master an Claude übergeben",
        "formDescription": "Einmalig für die PPTX-Erzeugung ohne Renderer.",
        "formFields": {"values": [
            form_field("ECOMEX-Master (.pptx)", "master", "file", required=True, multipleFiles=False, acceptFileTypes=".pptx,.potx"),
            form_field("Freigabe", "freigabe", "checkbox", required=True, fieldOptions=options(
                "Die Übermittlung des ECOMEX-Masters an Anthropic ist intern freigegeben.")),
        ]}, "responseMode": "onReceived",
        "options": {"path": "ecomex-master-claude", "buttonLabel": "Hochladen", "appendAttribution": False}},
        [0, 200], "Einstieg")
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_params([
        assign("nur_konfig", True, "boolean"),
    ], include_other=True), [220, 200], "nur Konfiguration anfordern")
    call(w, WF0, [440, 80], "API-Version aus der Konfiguration")
    w.node("Merge", "n8n-nodes-base.merge", 3.2, {"mode": "combine", "combineBy": "combineByPosition", "options": {}},
           [660, 200])
    http_anthropic(w, "HTTP Request", "POST", "https://api.anthropic.com/v1/files", "={{ $json.konfig.anthropic_version }}",
                   [880, 200], "Master hochladen", multipart="master", timeout=300000)
    w.node("Form", "n8n-nodes-base.form", 2.5, {
        "operation": "completion", "respondWith": "text", "completionTitle": "Master übergeben",
        "completionMessage": "={{ 'file_id: ' + $json.id + ' — bitte in ECOMEX 0 › Edit Fields › claude_master_file_id eintragen und speichern. (Datei: ' + ($json.filename || '') + ')' }}",
        "options": {}}, [1100, 200])
    w.chain("On form submission", "Edit Fields", f"Call '{WF0}'")
    w.link(f"Call '{WF0}'", "Merge", 0, 0)
    w.link("Edit Fields", "Merge", 0, 1)
    w.chain("Merge", "HTTP Request", "Form")
    w.save(OUT / "09_ECOMEX_Master_an_Claude.json")


# =================================================================================================
# ECOMEX 10 | Ablage einlesen (Supabase Storage → Wissensbasis)
# =================================================================================================
K0 = "$(\"Call 'ECOMEX 0 | Regelwerk & Katalog laden'\").first().json.konfig"

ABLAGE_AUSWAHL = r"""={{ (() => {
  const s = $('Edit Fields').first().json;
  const alle = $('HTTP Request').all().map(i => i.json).filter(o => o && o.object_path);
  const max = Number(s.max_mb || 60) * 1048576;
  const dateien = alle.filter(o => o.empfohlen && Number(o.bytes || 0) <= max);
  const zu_gross = alle.filter(o => o.empfohlen && Number(o.bytes || 0) > max);
  const nicht = alle.filter(o => !o.empfohlen);
  return { dateien, zu_gross, nicht_eingelesen: nicht, gesamt: alle.length, probelauf: s.probelauf === true || s.probelauf === 'true' };
})() }}"""

ABLAGE_DATEI = r"""={{ (() => {
  const f = $('Loop Over Items').first(1).json;
  const s = $('Edit Fields').first().json;
  const t = $json;
  const ordner = String(f.folder || '').split('/').filter(Boolean);
  const stamm = String(f.file_name || '').replace(/\.[^.]+$/, '').replace(/[_]+/g, ' ').trim();
  const sid = f.registered_source_id || f.source_id_vorschlag;
  return { source_id: sid, neu: !f.registered_source_id, titel: (ordner.length ? ordner[ordner.length - 1] + ' – ' : '') + stamm,
    source_type: t.source_type || f.source_type, storage_uri: f.storage_uri, dateiname: f.file_name,
    modul: ordner.length > 1 ? ordner[1] : (ordner[0] || ''), version: String(f.updated_at || '').slice(0, 10),
    review_status: s.review_status, access_class: s.access_class,
    license_note: 'Aus der Supabase-Ablage eingelesen – Lizenz/Nutzungsrechte prüfen; Fremdquellen nur sinngemäß nutzen.',
    abschnitte: (t.abschnitte || []).map(a => ({ content: a.text, locator: a.fundstelle })),
    notiz: (t.abschnitte_anzahl || 0) + ' Abschnitte, ' + (t.zeichen || 0) + ' Zeichen, gelesen per ' + (t.extraktion || '?') + '. ' + (t.hinweis || '') };
})() }}"""

ABLAGE_BERICHT = r"""={{ (() => {
  const a = $('Edit Fields1').first().json;
  const erg = $('Loop Over Items').isExecuted ? $('Loop Over Items').all(0).map(i => i.json) : [];
  const st = $('HTTP Request2').all().map(i => i.json).filter(o => o && o.review_status);
  const L = [];
  L.push('# Ablage einlesen · ' + $now.toFormat('dd.MM.yyyy HH:mm') + (a.probelauf ? ' · PROBELAUF (nichts geschrieben)' : ''));
  L.push('');
  L.push('Dateien in der Ablage: ' + a.gesamt + ' · ausgewählt: ' + a.dateien.length + ' · zu groß: ' + a.zu_gross.length + ' · nicht eingelesen: ' + a.nicht_eingelesen.length);
  if (erg.length) {
    L.push('');
    L.push('## Ergebnis');
    erg.forEach(e => L.push('- ' + (e.status === 'eingelesen' ? '✔' : '✖') + ' ' + e.datei + ' – ' + e.status + (e.chunks ? ' (' + e.chunks + ' Abschnitte, ' + e.source_id + ')' : '') + (e.hinweis ? ' · ' + e.hinweis : '')));
  } else if (a.probelauf) {
    L.push('');
    L.push('## Würde eingelesen');
    a.dateien.forEach(o => L.push('- ' + o.object_path + ' (' + (Number(o.bytes) / 1048576).toFixed(1) + ' MB) – ' + o.grund));
  }
  if (a.zu_gross.length) { L.push(''); L.push('## Zu groß (bitte als PDF exportieren oder max_mb erhöhen)'); a.zu_gross.forEach(o => L.push('- ' + o.object_path + ' (' + (Number(o.bytes) / 1048576).toFixed(0) + ' MB)')); }
  if (a.nicht_eingelesen.length) { L.push(''); L.push('## Nicht eingelesen'); a.nicht_eingelesen.forEach(o => L.push('- ' + o.object_path + ' – ' + o.grund)); }
  L.push('');
  L.push('## Wissensbasis jetzt');
  st.forEach(s => L.push('- ' + s.review_status + ': ' + s.quellen + ' Quellen, ' + s.chunks + ' Abschnitte' + (s.quellen_ohne_text ? ', davon ' + s.quellen_ohne_text + ' ohne Text' : '')));
  return { bericht: L.join('\n'), eingelesen: erg.filter(e => e.status === 'eingelesen').length, fehler: erg.filter(e => e.status !== 'eingelesen').length };
})() }}"""


def build_wf10():
    w = WF(WF10)
    w.sticky("info", "## ECOMEX 10 · Ablage einlesen (Supabase → Wissensbasis)\nLiest alle neuen Dateien aus dem Supabase-Bucket `ecomex-sources` in die Wissensbasis ein.\n\n"
             "1. **Edit Fields** anpassen: Ordner, Status, Zugriffsklasse, max. Größe, Probelauf.\n"
             "2. Starten mit *Execute workflow* (oder nachts per *Schedule Trigger*, dafür aktivieren).\n\n"
             "Die Datenbank entscheidet, was dran ist (`ecomex_storage_inventory`): neue Dateien; PPTX/Word nur, wenn keine PDF-Fassung im selben Ordner liegt; "
             "Folienmaster und Storyboards nie. Bereits eingelesene Dateien werden übersprungen → beliebig oft wiederholbar.\n\n"
             "Ergebnis: Bericht im letzten Node. Credentials: Supabase, OpenAI (Embeddings); Renderer optional.",
             [-560, -140], 520, 540, 4)
    w.node("When clicking ‘Execute workflow’", "n8n-nodes-base.manualTrigger", 1, {}, [0, 140])
    w.node("Schedule Trigger", "n8n-nodes-base.scheduleTrigger", 1.2, {
        "rule": {"interval": [{"field": "days", "daysInterval": 1, "triggerAtHour": 2}]}}, [0, 320],
        "nachts automatisch (bei Bedarf aktivieren)", disabled=True)
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_params([
        assign("nur_konfig", True, "boolean"),
        assign("ordner_praefix", ""),
        assign("review_status", "reference"),
        assign("access_class", "internal"),
        assign("max_mb", 60, "number"),
        assign("probelauf", False, "boolean"),
    ]), [240, 220], "EINSTELLUNGEN für den Import")
    call(w, WF0, [460, 220], "Konfiguration (Renderer da?)")
    http_supabase(w, "HTTP Request", "POST", "/rest/v1/rpc/ecomex_storage_inventory", [680, 220],
                  "Ablage-Inventar aus der Datenbank",
                  json_body="={{ JSON.stringify({ p_bucket: $json.konfig.supabase_bucket, p_prefix: $('Edit Fields').first().json.ordner_praefix || '' }) }}",
                  timeout=60000, alwaysOutputData=True)
    w.node("Edit Fields1", "n8n-nodes-base.set", 3.4, set_raw(ABLAGE_AUSWAHL), [900, 220], "Auswahl + Größenlimit",
           executeOnce=True)
    w.node("If", "n8n-nodes-base.if", 2.2, filter_params([
        cond("={{ !$json.probelauf && $json.dateien.length > 0 }}", "boolean", "true", single=True)]),
        [1120, 220], "einlesen?")
    w.node("Split Out", "n8n-nodes-base.splitOut", 1, {"fieldToSplitOut": "dateien", "include": "noOtherFields",
                                                       "options": {}}, [1340, 120], "eine Datei je Item")
    w.node("Loop Over Items", "n8n-nodes-base.splitInBatches", 3, {"batchSize": 1, "options": {}}, [1560, 120],
           "Datei für Datei")
    http_supabase(w, "HTTP Request1", "GET",
                  "/storage/v1/object/{{ " + K0 + ".supabase_bucket }}/{{ $json.object_path.split('/').map(p => encodeURIComponent(p)).join('/') }}",
                  [1800, 260], "Datei aus der Ablage laden", konfig=K0, file_out="datei", timeout=600000,
                  onError="continueErrorOutput")
    w.node("Edit Fields2", "n8n-nodes-base.set", 3.4, set_params([
        assign("dateiname", "={{ $('Loop Over Items').first(1).json.file_name }}"),
        assign("konfig", "={{ " + K0 + " }}", "object"),
    ], include_other=True), [2020, 200], "Kontext für die Textextraktion (Datei bleibt erhalten)")
    call(w, WF7, [2240, 200], "Datei → Text mit Fundstellen", onError="continueRegularOutput")
    w.node("Edit Fields3", "n8n-nodes-base.set", 3.4, set_raw(ABLAGE_DATEI), [2460, 200], "Quelle + Abschnitte")
    w.node("If1", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.abschnitte.length }}", "number", "gt", 0)]),
           [2680, 200], "Text gefunden?")
    w.node("If2", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.neu }}", "boolean", "true", single=True)]),
           [2900, 120], "neue Quelle?")
    w.node("Create a row", "n8n-nodes-base.supabase", 1, {
        "resource": "row", "operation": "create", "tableId": "ecomex_sources", "dataToSend": "defineBelow",
        "fieldsUi": {"fieldValues": [
            {"fieldId": "source_id", "fieldValue": "={{ $json.source_id }}"},
            {"fieldId": "title", "fieldValue": "={{ $json.titel }}"},
            {"fieldId": "source_type", "fieldValue": "={{ $json.source_type }}"},
            {"fieldId": "storage_provider", "fieldValue": "supabase_storage"},
            {"fieldId": "storage_uri", "fieldValue": "={{ $json.storage_uri }}"},
            {"fieldId": "module_id", "fieldValue": "={{ $json.modul || null }}"},
            {"fieldId": "review_status", "fieldValue": "={{ $json.review_status }}"},
            {"fieldId": "access_class", "fieldValue": "={{ $json.access_class }}"},
            {"fieldId": "version_label", "fieldValue": "={{ $json.version }}"},
            {"fieldId": "license_note", "fieldValue": "={{ $json.license_note }}"},
            {"fieldId": "notes", "fieldValue": "={{ $json.notiz }}"},
        ]}}, [3120, 40], "Quelle registrieren", onError="continueRegularOutput")
    w.node("Edit Fields4", "n8n-nodes-base.set", 3.4, set_params([
        assign("abschnitte", "={{ $('Edit Fields3').first().json.abschnitte }}", "array"),
    ]), [3340, 120], "Abschnitte")
    w.node("Split Out1", "n8n-nodes-base.splitOut", 1, {"fieldToSplitOut": "abschnitte", "include": "noOtherFields",
                                                        "options": {}}, [3560, 120])
    kb_nodes(w, 3800, 120, [(n, v.replace("$('Edit Fields2')", "$('Edit Fields3')")) for n, v in LOADER_METADATA])
    w.node("Aggregate", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateIndividualFields",
                                                        "fieldsToAggregate": {"fieldToAggregate": [{"fieldToAggregate": "pageContent"}]},
                                                        "options": {}}, [4040, 120])
    w.node("Edit Fields5", "n8n-nodes-base.set", 3.4, set_params([
        assign("datei", "={{ $('Edit Fields3').first().json.dateiname }}"),
        assign("status", "eingelesen"),
        assign("source_id", "={{ $('Edit Fields3').first().json.source_id }}"),
        assign("chunks", "={{ ($json.pageContent || []).length }}", "number"),
        assign("hinweis", "={{ $('Create a row').isExecuted && $('Create a row').first().json.error ? ('Registrierung: ' + String($('Create a row').first().json.error.message || $('Create a row').first().json.error).slice(0, 120)) : '' }}"),
    ]), [4260, 120], "Ergebnis: eingelesen")
    w.node("Edit Fields6", "n8n-nodes-base.set", 3.4, set_params([
        assign("datei", "={{ $('Loop Over Items').first(1).json.object_path }}"),
        assign("status", "übersprungen"),
        assign("source_id", ""),
        assign("chunks", 0, "number"),
        assign("hinweis", "={{ $json.error ? ('Download: ' + String($json.error.message || $json.error).slice(0, 160)) : ($json.notiz || $json.hinweis || 'kein Text') }}"),
    ]), [2900, 360], "Ergebnis: übersprungen")
    http_supabase(w, "HTTP Request2", "POST", "/rest/v1/rpc/ecomex_kb_status", [1800, 460], "Stand der Wissensbasis",
                  konfig=K0, json_body="={{ '{}' }}",
                  timeout=60000, executeOnce=True, alwaysOutputData=True)
    w.node("Edit Fields7", "n8n-nodes-base.set", 3.4, set_raw(ABLAGE_BERICHT), [2020, 560], "BERICHT", executeOnce=True)
    w.link("When clicking ‘Execute workflow’", "Edit Fields")
    w.link("Schedule Trigger", "Edit Fields")
    w.chain("Edit Fields", f"Call '{WF0}'", "HTTP Request", "Edit Fields1", "If")
    w.link("If", "Split Out", 0)
    w.link("If", "HTTP Request2", 1)
    w.link("Split Out", "Loop Over Items")
    w.link("Loop Over Items", "HTTP Request2", 0)
    w.link("Loop Over Items", "HTTP Request1", 1)
    w.link("HTTP Request1", "Edit Fields2", 0)
    w.link("HTTP Request1", "Edit Fields6", 1)
    w.chain("Edit Fields2", f"Call '{WF7}'", "Edit Fields3", "If1")
    w.link("If1", "If2", 0)
    w.link("If1", "Edit Fields6", 1)
    w.link("If2", "Create a row", 0)
    w.link("If2", "Edit Fields4", 1)
    w.link("Create a row", "Edit Fields4")
    w.link("Edit Fields4", "Split Out1")
    w.link("Split Out1", "Supabase Vector Store")
    w.chain("Supabase Vector Store", "Aggregate", "Edit Fields5")
    w.link("Edit Fields5", "Loop Over Items")
    w.link("Edit Fields6", "Loop Over Items")
    w.link("HTTP Request2", "Edit Fields7")
    w.save(OUT / "10_ECOMEX_Ablage_einlesen.json")
