"""Erzeugt die ECOMEX Content Factory v6 (mit und ohne Renderer) als importierbare n8n-Workflows (n8n 2.46+).

Node-Namen = Original-Namen der n8n-Bausteine; die Rolle steht als Notiz unter dem Node.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wf_lib import (WF, assign, cond, filter_params, form_field, options, rl_list, rl_name, set_params, set_raw,
                    sub_wf)
import prompts as P

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "workflows")
OUT.mkdir(parents=True, exist_ok=True)

WF0 = "ECOMEX 0 | Regelwerk & Katalog laden"
WF2 = "ECOMEX 2 | Tag produzieren"
WF3 = "ECOMEX 3 | Block produzieren"
TRIG = "When Executed by Another Workflow"
WF7 = "ECOMEX 7 | Text extrahieren"
WF8 = "ECOMEX 8 | PPTX ohne Renderer (Claude)"
WF9 = "ECOMEX 9 | Master an Claude übergeben"
WF10 = "ECOMEX 10 | Ablage einlesen (Supabase)"

OPUS = rl_list("claude-opus-5-5", "Claude Opus 5.5")
SONNET = rl_list("claude-sonnet-5-5", "Claude Sonnet 5.5")
GPT = rl_list("gpt-5.5", "gpt-5.5")


def anthropic_model(wf, name, model, pos, effort="high", max_tokens=32000, note=None, cache="1h"):
    # Regelwerk steht im System-Prompt und ist für alle Blöcke eines Tages gleich -> 1h-Cache spart Kosten
    return wf.node(name, "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.6,
                   {"model": model, "options": {"maxTokensToSample": max_tokens, "thinkingMode": "adaptive",
                                                "effort": effort, "streaming": True, "promptCaching": cache}},
                   pos, note)


def openai_model(wf, name, pos, web=True, effort="medium", note=None):
    p = {"model": GPT, "responsesApiEnabled": True,
         "options": {"reasoningEffort": effort, "timeout": 600000, "maxRetries": 2}}
    if web:
        p["builtInTools"] = {"webSearch": {"searchContextSize": "high"}}
    return wf.node(name, "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.3, p, pos, note)


def parser(wf, name, schema, pos):
    return wf.node(name, "@n8n/n8n-nodes-langchain.outputParserStructured", 1.3,
                   {"schemaType": "manual", "inputSchema": json.dumps(schema, ensure_ascii=False, indent=1)}, pos)


def chain(wf, name, system, user, pos, note):
    return wf.node(name, "@n8n/n8n-nodes-langchain.chainLlm", 1.9,
                   {"promptType": "define", "text": user, "hasOutputParser": True,
                    "messages": {"messageValues": [{"type": "SystemMessagePromptTemplate", "message": system}]}},
                   pos, note, retryOnFail=True, maxTries=2, waitBetweenTries=5000)


def http_renderer(wf, name, path_expr, pos, note, method="POST", body_expr=None, file_out=None, multipart=None,
                  timeout=300000, base="$json.konfig.renderer_url"):
    p = {"method": method, "url": "={{ " + base + " }}" + path_expr,
         "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth", "options": {"timeout": timeout}}
    if body_expr:
        p.update({"sendBody": True, "specifyBody": "json", "jsonBody": body_expr})
    if multipart:
        p.update({"sendBody": True, "contentType": "multipart-form-data",
                  "bodyParameters": {"parameters": [{"parameterType": "formBinaryData", "name": "file",
                                                     "inputDataFieldName": multipart}]}})
    if file_out:
        p["options"]["response"] = {"response": {"responseFormat": "file", "outputPropertyName": file_out}}
    return wf.node(name, "n8n-nodes-base.httpRequest", 4.2, p, pos, note)


def call(w, wf_name, pos, note, mode="once", wait=True, **extra):
    """Execute-Workflow-Node in n8n-Standardbenennung: Call '<Workflow>'."""
    return w.node(f"Call '{wf_name}'", "n8n-nodes-base.executeWorkflow", 1.3, {
        "source": "database", "workflowId": sub_wf(wf_name), "mode": mode, "options": {"waitForSubWorkflow": wait}},
        pos, note, **extra)


def http_supabase(w, name, method, path_expr, pos, note, konfig="$json.konfig", json_body=None, file_out=None,
                  binary_in=None, headers=None, timeout=300000, **extra):
    """HTTP Request mit dem Supabase-Credential (Service-Role) gegen REST/Storage der Content-Factory-Datenbank."""
    p = {"method": method, "url": "={{ " + konfig + ".supabase_url }}" + path_expr,
         "authentication": "predefinedCredentialType", "nodeCredentialType": "supabaseApi", "options": {"timeout": timeout}}
    if headers:
        p.update({"sendHeaders": True, "headerParameters": {"parameters": [{"name": k, "value": v} for k, v in headers]}})
    if json_body:
        p.update({"sendBody": True, "specifyBody": "json", "jsonBody": json_body})
    if binary_in:
        p.update({"sendBody": True, "contentType": "binaryData", "inputDataFieldName": binary_in})
    if file_out:
        p["options"]["response"] = {"response": {"responseFormat": "file", "outputPropertyName": file_out}}
    return w.node(name, "n8n-nodes-base.httpRequest", 4.2, p, pos, note, **extra)


def http_anthropic(w, name, method, url_expr, version_expr, pos, note, json_body=None, file_out=None, multipart=None,
                   timeout=600000, **extra):
    """HTTP Request mit dem vorhandenen Anthropic-Credential (x-api-key) + anthropic-version."""
    p = {"method": method, "url": url_expr, "authentication": "predefinedCredentialType", "nodeCredentialType": "anthropicApi",
         "sendHeaders": True, "headerParameters": {"parameters": [{"name": "anthropic-version", "value": version_expr}]},
         "options": {"timeout": timeout}}
    if json_body:
        p.update({"sendBody": True, "specifyBody": "json", "jsonBody": json_body})
    if multipart:
        p.update({"sendBody": True, "contentType": "multipart-form-data",
                  "bodyParameters": {"parameters": [{"parameterType": "formBinaryData", "name": "file",
                                                     "inputDataFieldName": multipart}]}})
    if file_out:
        p["options"]["response"] = {"response": {"responseFormat": "file", "outputPropertyName": file_out}}
    return w.node(name, "n8n-nodes-base.httpRequest", 4.2, p, pos, note, **extra)


# =================================================================================================
# ECOMEX 1 | Neues Kursdeck (Start)
# =================================================================================================
def build_wf1():
    w = WF("ECOMEX 1 | Neues Kursdeck (Start)")
    w.sticky("info", "## ECOMEX 1 · Neues Kursdeck\n**Der einzige Einstieg.** Formular öffnen (Produktions-URL), ausfüllen, absenden.\n\n"
             "**A** Vorhandenes Storyboard (Word/Excel/PDF) → KI strukturiert es → Vorschau.\n"
             "**B** Idee → KI entwickelt ein Storyboard → Vorschau.\n"
             "**C** Freigegebenes ECOMEX-Storyboard (Excel-Vorlage) → direkt Produktion.\n\n"
             "In der Vorschau: *Freigeben & produzieren*, *Überarbeiten lassen* oder *Nur herunterladen*.\n"
             "Jeder Tag wird parallel als eigenes Deck produziert (Workflow 2). Ergebnis: PPTX, QA-Bericht, Manuskript, Deckdaten (mit Renderer zusätzlich PDF-Vorschau).\n\n"
             "Einmalig: die drei **Call**-Nodes auf die importierten Workflows stellen; Credentials wählen.",
             [-560, -120], 500, 520, 4)
    w.node("On form submission", "n8n-nodes-base.formTrigger", 2.6, {
        "authentication": "n8nUserAuth",
        "formTitle": "ECOMEX Content Factory · Neues Kursdeck",
        "formDescription": "Storyboard hochladen oder Idee beschreiben. Ergebnisse sind immer ENTWÜRFE und gehen erst nach menschlicher Freigabe in den Unterricht.",
        "formFields": {"values": [
            form_field("Modul", "modul", required=True, placeholder="z. B. M02 oder KI-Strategie"),
            form_field("Tag(e) / Abschnitt", "tage", required=True, placeholder="z. B. Tag 12 oder Tag 12–16"),
            form_field("Kursthema", "thema", required=True, placeholder="z. B. KI-Arbeitsabläufe testen"),
            form_field("Zielgruppe / Vorwissen", "zielgruppe", "textarea",
                       defaultValue="Heterogene, berufserfahrene Erwachsene mit sehr unterschiedlichen IT-Vorkenntnissen"),
            form_field("Ausgangslage", "ausgangslage", "radio", required=True, fieldOptions=options(
                "A – Vorhandenes Storyboard (Word/Excel/PDF) auswerten",
                "B – Storyboard aus Idee entwickeln",
                "C – Freigegebenes ECOMEX-Storyboard (Excel-Vorlage) direkt produzieren")),
            form_field("Storyboard-Datei (bei A und C)", "datei", "file", multipleFiles=False,
                       acceptFileTypes=".docx,.xlsx,.pdf,.pptx,.txt,.md"),
            form_field("Briefing / Idee / Ergänzungen", "briefing", "textarea",
                       placeholder="Lernziele, Schwerpunkte, Fallbeispiel, was auf keinen Fall fehlen darf …"),
            form_field("Folien pro Tag (Zielwert)", "folien_pro_tag", "number", defaultValue="45"),
            form_field("Freigabe externe KI", "freigabe", "checkbox", required=True, fieldOptions=options(
                "Die Verarbeitung dieser Inhalte mit externen KI-Diensten (Anthropic, OpenAI) ist intern freigegeben.")),
        ]},
        "responseMode": "onReceived",
        "options": {"path": "ecomex-kursdeck", "buttonLabel": "Weiter", "appendAttribution": False}},
        [0, 200], "Einstieg: Formular")
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_params([
        assign("run_id", "={{ 'ECX-' + $now.toFormat('yyyyLLdd-HHmm') + '-' + $execution.id }}"),
        assign("modul", "={{ $json.modul.trim() }}"),
        assign("tage", "={{ $json.tage.trim() }}"),
        assign("thema", "={{ $json.thema.trim() }}"),
        assign("zielgruppe", "={{ $json.zielgruppe || 'Heterogene, berufserfahrene Erwachsene' }}"),
        assign("modus", "={{ $json.ausgangslage.startsWith('C') ? 'FREIGEGEBEN' : ($json.ausgangslage.startsWith('A') ? 'STORYBOARD' : 'IDEE') }}"),
        assign("folien_pro_tag", "={{ Math.min(70, Math.max(10, Number($json.folien_pro_tag) || 45)) }}", "number"),
        assign("briefing", "={{ $json.briefing || '' }}"),
        assign("hat_datei", "={{ $binary.datei !== undefined }}", "boolean"),
        assign("erstellt_von", "={{ ($json.user && $json.user.email) || '' }}"),
    ], include_other=True), [240, 200], "Produktionsauftrag (Datei bleibt erhalten)")
    call(w, WF0, [480, 80], "Regeln + Katalog + Konfiguration LIVE")
    w.node("Merge", "n8n-nodes-base.merge", 3.2, {"mode": "combine", "combineBy": "combineByPosition", "options": {}},
           [720, 200], "Auftrag + Regeln + Datei")
    w.node("If", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.modus }}", "string", "equals", "FREIGEGEBEN")]),
           [940, 200], "C: freigegebenes Excel?")
    # --- Pfad C
    w.node("Extract from XLSX", "n8n-nodes-base.extractFromFile", 1, {"operation": "xlsx", "binaryPropertyName": "datei",
                                                                    "options": {}}, [1180, -40], "Excel-Storyboard lesen")
    w.node("Aggregate", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateAllItemData",
                                                        "destinationFieldName": "alle_zeilen", "options": {}},
           [1400, -40])
    w.node("Edit Fields1", "n8n-nodes-base.set", 3.4, set_params([
        assign("zeilen", "={{ $json.alle_zeilen.filter(z => /freigegeben/i.test(String(z.Status || ''))) }}", "array"),
        assign("storyboard_titel", "={{ $('Merge').first().json.thema }}"),
    ]), [1620, -40], "nur Status 'Freigegeben'")
    w.node("If2", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.zeilen.length }}", "number", "gt", 0)]),
           [1840, -40], "freigegebene Zeilen vorhanden?")
    w.node("Stop and Error", "n8n-nodes-base.stopAndError", 1, {
        "errorMessage": "Im Excel-Storyboard gibt es keine Zeile mit Status 'Freigegeben'. Bitte Vorlage prüfen (Spaltennamen nicht ändern)."},
        [2060, 80])
    # --- Pfad A/B
    w.node("If1", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.hat_datei }}", "boolean", "true", single=True)]),
           [1180, 420], "Datei hochgeladen?")
    call(w, WF7, [1400, 340], "Datei → Text mit Fundstellen (Renderer oder n8n)")
    chain(w, "Basic LLM Chain", P.STORYBOARD_SYSTEM, P.STORYBOARD_USER, [1660, 440], "Storyboard-Redaktion (Claude)")
    anthropic_model(w, "Anthropic Chat Model", OPUS, [1600, 680], effort="high", cache="5m")
    parser(w, "Structured Output Parser", P.STORYBOARD_SCHEMA, [1800, 680])
    w.node("Edit Fields2", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const sb = $json.output;
  const e = s => String(s == null ? '' : s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' })[c]);
  const tage = [...new Set(sb.bloecke.map(b => String(b.Tag)))];
  let h = '<h2>' + e(sb.titel) + '</h2><p>' + e(sb.zusammenfassung) + '</p>';
  tage.forEach(t => {
    const bl = sb.bloecke.filter(b => String(b.Tag) === t);
    const sum = bl.reduce((a, b) => a + (Number(b.Folien) || 0), 0);
    h += '<h3>' + e(t) + ' · ' + bl.length + ' Blöcke · ' + sum + ' Folien</h3><table><tr><th>Zeit</th><th>Lerneinheit</th><th>Art</th><th>Folien</th></tr>';
    bl.forEach(b => {
      h += '<tr><td>' + e(b.Von) + '–' + e(b.Bis) + '</td><td><b>' + e(b.Titel) + '</b><br><small>' + e(b.Lernziele) + '</small>'
        + (b.Offene_Fragen ? '<br><small>⚠ ' + e(b.Offene_Fragen) + '</small>' : '') + '</td><td>' + e(b.Art) + '</td><td>' + e(b.Folien) + '</td></tr>';
    });
    h += '</table>';
  });
  if ((sb.annahmen || []).length) h += '<h3>Annahmen der KI</h3><ul>' + sb.annahmen.map(a => '<li>' + e(a) + '</li>').join('') + '</ul>';
  if ((sb.offene_fragen || []).length) h += '<h3>Offene Fragen</h3><ul>' + sb.offene_fragen.map(a => '<li>' + e(a) + '</li>').join('') + '</ul>';
  return { storyboard: sb, vorschau_html: h };
})() }}""", include_binary=False), [2000, 440], "Vorschau aufbereiten")
    w.node("Form", "n8n-nodes-base.form", 2.5, {
        "operation": "page", "defineForm": "fields",
        "formFields": {"values": [
            {"fieldLabel": "Vorschau", "fieldType": "html", "html": "={{ $json.vorschau_html }}"},
            form_field("Entscheidung", "entscheidung", "radio", required=True, fieldOptions=options(
                "Freigeben und Produktion starten",
                "Überarbeiten lassen (Hinweise unten)",
                "Nur als Excel herunterladen (ich bearbeite selbst und starte später mit C)")),
            form_field("Änderungswünsche", "aenderungen", "textarea",
                       placeholder="z. B. Block 3 kürzer, Übung zu Datenschutz ergänzen, Freitag endet 13:00 …"),
        ]},
        "options": {"formTitle": "Storyboard prüfen", "buttonLabel": "Weiter",
                    "formDescription": "Bitte prüfen. Erst nach Freigabe werden Folien produziert."}},
        [2240, 440], "Mensch prüft Storyboard")
    w.node("If3", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.entscheidung }}", "string", "startsWith", "Überarbeiten")]),
           [2460, 440], "überarbeiten?")
    chain(w, "Basic LLM Chain1", P.STORYBOARD_SYSTEM, P.STORYBOARD_REVISE_USER, [2700, 640], "Storyboard überarbeiten")
    anthropic_model(w, "Anthropic Chat Model1", OPUS, [2640, 880], effort="medium", cache="5m")
    parser(w, "Structured Output Parser1", P.STORYBOARD_SCHEMA, [2800, 880])
    w.node("If4", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.entscheidung }}", "string", "startsWith", "Freigeben")]),
           [2700, 340], "freigeben & produzieren?")
    w.node("Edit Fields3", "n8n-nodes-base.set", 3.4, set_params([
        assign("zeilen", "={{ $('Edit Fields2').last().json.storyboard.bloecke }}", "array"),
        assign("storyboard_titel", "={{ $('Edit Fields2').last().json.storyboard.titel }}"),
        assign("freigabe_kommentar", "={{ $json.aenderungen || '' }}"),
    ]), [2940, 240], "freigegebenes Storyboard")
    # --- Produktion
    w.node("Edit Fields4", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const job = $('Merge').first().json;
  const zeilen = $json.zeilen.map(z => ({ ...z, Status: 'Freigegeben' }));
  const tage = [...new Set(zeilen.map(z => String(z.Tag).trim()))];
  return {
    zeilen,
    tage: tage.map(t => ({
      run_id: job.run_id, modul: job.modul, thema: job.thema, zielgruppe: job.zielgruppe,
      folien_pro_tag: job.folien_pro_tag, storyboard_titel: $json.storyboard_titel || job.thema, erstellt_von: job.erstellt_von,
      tag: t, zeilen: zeilen.filter(z => String(z.Tag).trim() === t),
      regeln: job.regeln, regel_versionen: job.regel_versionen, katalog: job.katalog, konfig: job.konfig
    }))
  };
})() }}""", include_binary=False), [3180, 0], "ein Auftrag pro Tag")
    w.node("Split Out", "n8n-nodes-base.splitOut", 1, {"fieldToSplitOut": "tage", "include": "noOtherFields",
                                                       "options": {}}, [3400, 0])
    call(w, WF2, [3620, 0], "Tage parallel produzieren (läuft im Hintergrund)", mode="each", wait=False)
    w.node("Aggregate1", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateIndividualFields",
                                                         "fieldsToAggregate": {"fieldToAggregate": [{"fieldToAggregate": "tag"}]},
                                                         "options": {}}, [3840, 0], "gestartete Tage")
    w.node("Edit Fields5", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const prod = $('Edit Fields4').isExecuted;
  const zeilen = prod ? $('Edit Fields4').first().json.zeilen : $('Edit Fields2').last().json.storyboard.bloecke;
  const status = prod ? 'Freigegeben' : 'Entwurf';
  return { zeilen: zeilen.map(z => ({ Tag: z.Tag || '', Datum: z.Datum || '', Block: z.Block, Von: z.Von, Bis: z.Bis, Titel: z.Titel,
    Art: z.Art, Lernziele: z.Lernziele || '', Inhalte: z.Inhalte || '', Methode: z.Methode || '', Material: z.Material || '',
    Folien: z.Folien, Quellen: z.Quellen || '', Hinweise: z.Hinweise || '', Fundstellen: z.Fundstellen || '', Status: status,
    Offene_Fragen: z.Offene_Fragen || '' })) };
})() }}""", include_binary=False), [4060, 240], "Excel-Zeilen (Vorlagenformat)")
    w.node("Split Out1", "n8n-nodes-base.splitOut", 1, {"fieldToSplitOut": "zeilen", "include": "noOtherFields",
                                                        "options": {}}, [4280, 240])
    w.node("Convert to XLSX", "n8n-nodes-base.convertToFile", 1.1, {
        "operation": "xlsx", "binaryPropertyName": "data",
        "options": {"fileName": "={{ 'ECOMEX_Storyboard_' + $('Merge').first().json.modul + '_' + $('Merge').first().json.tage.replace(/[^A-Za-z0-9]+/g, '_') + '.xlsx' }}",
                    "sheetName": "Storyboard", "headerRow": True}}, [4500, 240], "Storyboard als Excel")
    w.node("Form1", "n8n-nodes-base.form", 2.5, {
        "operation": "completion", "respondWith": "returnBinary", "inputDataFieldName": "data",
        "completionTitle": "={{ $('Edit Fields4').isExecuted ? 'Produktion gestartet' : 'Storyboard bereit' }}",
        "completionMessage": "={{ $('Edit Fields4').isExecuted ? ('Die Produktion läuft im Hintergrund für: ' + $('Edit Fields4').first().json.tage.map(t => t.tag).join(', ') + '. Pro Tag entstehen PPTX (mit Renderer zusätzlich PDF-Vorschau), QA-Bericht, Folien-Manuskript und Deckdaten (n8n-Ausführungen von „ECOMEX 2“ bzw. SharePoint). Dauer je Tag ca. 30–60 Minuten. Run-ID: ' + $('Merge').first().json.run_id) : 'Das Storyboard wird heruntergeladen. Bearbeiten, Status auf „Freigegeben“ setzen und mit Ausgangslage C starten.' }}",
        "options": {}}, [4720, 240], "Excel herunterladen + Status")
    # Verbindungen
    w.link("On form submission", "Edit Fields")
    w.link("Edit Fields", f"Call '{WF0}'")
    w.link(f"Call '{WF0}'", "Merge", 0, 0)
    w.link("Edit Fields", "Merge", 0, 1)
    w.link("Merge", "If")
    w.link("If", "Extract from XLSX", 0)
    w.link("If", "If1", 1)
    w.chain("Extract from XLSX", "Aggregate", "Edit Fields1", "If2")
    w.link("If2", "Edit Fields4", 0)
    w.link("If2", "Stop and Error", 1)
    w.link("If1", f"Call '{WF7}'", 0)
    w.link("If1", "Basic LLM Chain", 1)
    w.link(f"Call '{WF7}'", "Basic LLM Chain")
    w.ai("Anthropic Chat Model", "Basic LLM Chain", "ai_languageModel")
    w.ai("Structured Output Parser", "Basic LLM Chain", "ai_outputParser")
    w.chain("Basic LLM Chain", "Edit Fields2", "Form", "If3")
    w.link("If3", "Basic LLM Chain1", 0)
    w.link("If3", "If4", 1)
    w.ai("Anthropic Chat Model1", "Basic LLM Chain1", "ai_languageModel")
    w.ai("Structured Output Parser1", "Basic LLM Chain1", "ai_outputParser")
    w.link("Basic LLM Chain1", "Edit Fields2")
    w.link("If4", "Edit Fields3", 0)
    w.link("If4", "Edit Fields5", 1)
    w.chain("Edit Fields3", "Edit Fields4", "Split Out", f"Call '{WF2}'", "Aggregate1", "Edit Fields5", "Split Out1",
            "Convert to XLSX", "Form1")
    w.sticky("c", "### Pfad C\nFreigegebenes Excel (Vorlage) → nur Zeilen mit Status *Freigegeben*.", [1160, -220], 900, 150, 5)
    w.sticky("ab", "### Pfad A / B\nDatei → Text mit Fundstellen (**ECOMEX 7**: Renderer oder n8n) → Storyboard-Redaktion (Claude Opus) → Vorschau → Entscheidung. "
             "„Überarbeiten“ läuft so oft wie nötig.", [1160, 1000], 1780, 140, 5)
    w.sticky("prod", "### Produktion\nPro Tag ein Auftrag an **ECOMEX 2** – parallel, im Hintergrund. Das Formular antwortet sofort mit dem Storyboard als Excel.",
             [3160, -200], 1780, 150, 6)
    w.save(OUT / "01_ECOMEX_Neues_Kursdeck_START.json")


# =================================================================================================
# ECOMEX 3 | Block produzieren (Multi-Agenten-Kern)
# =================================================================================================
def build_wf3():
    w = WF(WF3)
    w.sticky("info", "## ECOMEX 3 · Block produzieren (Agenten-Team)\nEine Lerneinheit = ein Lauf. Aufgerufen von ECOMEX 2 und ECOMEX 4.\n\n"
             "**Recherche** (GPT + Websuche, interne Fundstellen aus Supabase – Status *approved*, und *reference*, solange in ECOMEX 0 erlaubt)\n→ **Fachdidaktik** (Claude Opus: Inhalt, Übungen, Sprechertext)\n"
             "→ **Layout** (Claude Sonnet: Katalog-Layouts, Zeichenlimits)\n→ **QA** (GPT + Websuche, unabhängig)\n"
             "→ bei Mängeln **Revision** (Claude Opus), max. 1 Runde.\n\nPausen werden ohne KI gesetzt.\n"
             "Regeln aus GitHub stehen in jedem System-Prompt (Prompt-Caching aktiv).", [-560, -100], 500, 460, 4)
    w.node(TRIG, "n8n-nodes-base.executeWorkflowTrigger", 1.1, {"inputSource": "passthrough"}, [0, 300])
    w.node("If", "n8n-nodes-base.if", 2.2, filter_params([
        cond("={{ String($json.zeile.Art || '').toLowerCase().trim() }}", "string", "equals", "pause")]),
        [220, 300], "Pause?")
    w.node("Edit Fields", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const z = $json.zeile;
  const min = s => { const p = String(s || '').split(':').map(Number); return (p[0] || 0) * 60 + (p[1] || 0); };
  const d = min(z.Bis) - min(z.Von);
  return { block: z.Block, titel: z.Titel, quellen: [], qa: { status: 'OHNE_KI', befunde: [] },
    folien: [{ layout: 'pause', block: 'Block ' + z.Block, felder: { titel: z.Titel || 'Pause', dauer: d > 0 ? d + ' Min.' : '', text: z.Bis ? 'Weiter geht es um ' + z.Bis + ' Uhr.' : '' },
      notizen: 'Pause.' }] };
})() }}""", include_binary=False), [460, 100], "Pausenfolie ohne KI")
    w.node("Supabase Vector Store", "@n8n/n8n-nodes-langchain.vectorStoreSupabase", 1.3, {
        "mode": "load", "tableName": {"__rl": True, "mode": "id", "value": "ecomex_documents"},
        "prompt": "={{ [$json.thema, $json.zeile.Titel, $json.zeile.Inhalte, $json.zeile.Lernziele].filter(Boolean).join(' · ') }}",
        "topK": 8, "includeDocumentMetadata": True, "options": {"queryName": "ecomex_match_documents", "metadata": {
            "metadataValues": [{"name": "allow_reference", "value": "={{ String(!$json.konfig || $json.konfig.wissensbasis_referenzen !== false) }}"}]}}},
        [460, 440], "interne Fundstellen (RAG)", onError="continueRegularOutput", alwaysOutputData=True)
    w.node("Embeddings OpenAI", "@n8n/n8n-nodes-langchain.embeddingsOpenAi", 1.2,
           {"model": "text-embedding-3-small", "options": {}}, [480, 660])
    w.node("Aggregate", "n8n-nodes-base.aggregate", 1, {"aggregate": "aggregateAllItemData",
                                                        "destinationFieldName": "treffer", "options": {}}, [700, 440])
    w.node("Edit Fields1", "n8n-nodes-base.set", 3.4, set_params([
        assign("fundstellen_text", r"""={{ (($json.treffer || []).filter(t => t.document && t.document.pageContent).map((t, i) => '[' + (i + 1) + '] ' + ((t.document.metadata || {}).title || 'ohne Titel') + ' · ' + ((t.document.metadata || {}).locator || '') + ' · ' + ((t.document.metadata || {}).source_uri || '') + ' · Relevanz ' + (t.score ? Number(t.score).toFixed(2) : '?') + '\n' + String(t.document.pageContent).slice(0, 2500)).join('\n\n')) || 'Keine internen Fundstellen (Wissensbasis leer oder nicht verbunden).' }}"""),
        assign("anzahl_fundstellen", "={{ ($json.treffer || []).filter(t => t.document).length }}", "number"),
    ]), [920, 440], "Fundstellen aufbereiten")
    chain(w, "Basic LLM Chain", P.RECHERCHE_SYSTEM, P.RECHERCHE_USER, [1160, 440], "1 · Recherche-Agent (GPT + Websuche)")
    openai_model(w, "OpenAI Chat Model", [1100, 680], web=True, effort="medium")
    parser(w, "Structured Output Parser", P.RECHERCHE_SCHEMA, [1260, 680])
    chain(w, "Basic LLM Chain1", P.CONTENT_SYSTEM, P.CONTENT_USER, [1500, 440], "2 · Fachdidaktik-Agent (Claude Opus)")
    anthropic_model(w, "Anthropic Chat Model", OPUS, [1440, 680], effort="high", max_tokens=48000)
    parser(w, "Structured Output Parser1", P.CONTENT_SCHEMA, [1600, 680])
    chain(w, "Basic LLM Chain2", P.LAYOUT_SYSTEM, P.LAYOUT_USER, [1840, 440], "3 · Layout-Agent (Claude Sonnet)")
    anthropic_model(w, "Anthropic Chat Model1", SONNET, [1780, 680], effort="medium", max_tokens=32000)
    parser(w, "Structured Output Parser2", P.LAYOUT_SCHEMA, [1940, 680])
    chain(w, "Basic LLM Chain3", P.QA_SYSTEM, P.QA_USER, [2180, 440], "4 · QA-Agent (GPT + Websuche, unabhängig)")
    openai_model(w, "OpenAI Chat Model1", [2120, 680], web=True, effort="high")
    parser(w, "Structured Output Parser3", P.QA_SCHEMA, [2280, 680])
    w.node("If1", "n8n-nodes-base.if", 2.2, filter_params([cond("={{ $json.output.status }}", "string", "equals", "UEBERARBEITEN")]),
           [2420, 440], "Mängel gefunden?")
    chain(w, "Basic LLM Chain4", P.REVISION_SYSTEM, P.REVISION_USER, [2660, 300], "5 · Revisions-Agent (Claude Opus)")
    anthropic_model(w, "Anthropic Chat Model2", OPUS, [2600, 80], effort="medium", max_tokens=32000)
    parser(w, "Structured Output Parser4", P.LAYOUT_SCHEMA, [2760, 80])
    w.node("Edit Fields2", "n8n-nodes-base.set", 3.4, set_raw(r"""={{ (() => {
  const job = $('When Executed by Another Workflow').first().json;
  const z = job.zeile;
  const rev = $('Basic LLM Chain4').isExecuted;
  const design = rev ? $('Basic LLM Chain4').first().json.output : $('Basic LLM Chain2').first().json.output;
  const qa = $('Basic LLM Chain3').first().json.output;
  const rech = $('Basic LLM Chain').first().json.output;
  const label = 'Block ' + z.Block;
  return {
    block: z.Block, titel: z.Titel, von: z.Von, bis: z.Bis,
    folien: (design.folien || []).map(f => ({ ...f, block: label })),
    qa: { status: rev ? 'UEBERARBEITET' : qa.status, befunde: qa.befunde || [], nicht_behoben: rev ? (design.nicht_behoben || []) : [],
          offene_punkte: [...($('Basic LLM Chain1').first().json.output.offene_punkte || []), ...(qa.offene_punkte || [])] },
    quellen: rech.quellen || [],
    interne_fundstellen: $('Edit Fields1').first().json.anzahl_fundstellen
  };
})() }}""", include_binary=False), [2900, 440], "Blockergebnis")
    for key, x, txt in (
            ("a1", 1060, "**1 · Recherche** – GPT-5.5 mit Websuche (OpenAI-Credential). Wertet interne Fundstellen und aktuelle Primärquellen aus; Aussagen mit Beleg, Datum, Sicherheit."),
            ("a2", 1400, "**2 · Fachdidaktik** – Claude Opus 5.5 (Anthropic-Credential). Inhalt, Übungen mit Material + Musterlösung, Sprechertext – nach didaktik.md."),
            ("a3", 1740, "**3 · Layout** – Claude Sonnet 5.5. Wählt Layouts aus dem Katalog, hält Zeichenlimits ein, verändert keine Inhalte."),
            ("a4", 2080, "**4 · QA** – GPT-5.5 + Websuche, bewusst anderer Anbieter als die Autorin. Prüft gegen qa_rules.md; blocker/major → Revision.")):
        w.sticky(key, txt, [x, 220], 310, 190, 7)
    w.sticky("a5", "**5 · Revision** – Claude Opus 5.5, max. 1 Runde. Was nicht lösbar ist, bleibt im QA-Bericht sichtbar.",
             [2560, -140], 330, 170, 7)
    w.link(TRIG, "If")
    w.link("If", "Edit Fields", 0)
    w.link("If", "Supabase Vector Store", 1)
    w.ai("Embeddings OpenAI", "Supabase Vector Store", "ai_embedding")
    w.chain("Supabase Vector Store", "Aggregate", "Edit Fields1", "Basic LLM Chain", "Basic LLM Chain1",
            "Basic LLM Chain2", "Basic LLM Chain3", "If1")
    for m, c in (("OpenAI Chat Model", "Basic LLM Chain"), ("Anthropic Chat Model", "Basic LLM Chain1"),
                 ("Anthropic Chat Model1", "Basic LLM Chain2"), ("OpenAI Chat Model1", "Basic LLM Chain3"),
                 ("Anthropic Chat Model2", "Basic LLM Chain4")):
        w.ai(m, c, "ai_languageModel")
    for p_, c in (("Structured Output Parser", "Basic LLM Chain"), ("Structured Output Parser1", "Basic LLM Chain1"),
                  ("Structured Output Parser2", "Basic LLM Chain2"), ("Structured Output Parser3", "Basic LLM Chain3"),
                  ("Structured Output Parser4", "Basic LLM Chain4")):
        w.ai(p_, c, "ai_outputParser")
    w.link("If1", "Basic LLM Chain4", 0)
    w.link("If1", "Edit Fields2", 1)
    w.link("Basic LLM Chain4", "Edit Fields2")
    w.save(OUT / "03_ECOMEX_Block_produzieren_AGENTEN.json")




DECK_ZUSAMMENSETZEN = r"""={{ (() => {
  const job = $('Edit Fields').first().json;
  const zeilen = job.zeilen;
  const bl = $json.bloecke || [];
  const ziele = zeilen.filter(z => String(z.Art).toLowerCase() !== 'pause')
    .flatMap(z => String(z.Lernziele || '').split(';')).map(s => s.trim()).filter(Boolean);
  const folien = [
    { layout: 'titel', felder: { titel: job.thema, untertitel: job.storyboard_titel && job.storyboard_titel !== job.thema ? job.storyboard_titel : '', meta: [job.modul, job.tag].filter(Boolean).join(' · ') } },
    { layout: 'tagesablauf', felder: { titel: 'Unser Tag', eintraege: zeilen.map(z => ({ zeit: z.Von + '–' + z.Bis, titel: z.Titel, art: String(z.Art || 'input').toLowerCase() })) },
      notizen: 'Tagesablauf kurz vorstellen: Wo stehen wir in der Kurswoche, was ist das Ziel des Tages, wann sind Pausen und Übungen?' },
    { layout: 'lernziele', felder: { titel: 'Heute lernen Sie …', ziele: [...new Set(ziele)].slice(0, 5) },
      notizen: 'Lernziele vorlesen lassen oder kurz erläutern. Fragen: Welches Ziel ist für Ihren Arbeitsalltag am wichtigsten?' }
  ];
  bl.forEach((b, i) => {
    if (b && Array.isArray(b.folien) && b.folien.length) { folien.push(...b.folien); return; }
    const z = zeilen[i] || {};
    folien.push({ layout: 'kernaussage', block: 'Block ' + z.Block, felder: { titel: z.Titel || 'Block ' + z.Block,
      aussage: 'Dieser Block konnte nicht automatisch erzeugt werden.',
      erlaeuterung: 'Bitte mit „ECOMEX 4 | Deck überarbeiten“ (Block ' + z.Block + ' neu erzeugen) nachholen. ' + String((b && b.error) || '').slice(0, 120) },
      notizen: 'Platzhalter für fehlgeschlagenen Block.', review_hinweise: ['Block fehlt – neu erzeugen'] });
  });
  return {
    deck: { meta: { modul: job.modul, tag: job.tag, thema: job.thema, zielgruppe: job.zielgruppe, run_id: job.run_id, entwurf: true,
      dateiname: ['ECOMEX', job.modul, job.tag, 'ENTWURF'].join('_'), storyboard_titel: job.storyboard_titel,
      storyboard_zeilen: zeilen, regel_versionen: job.regel_versionen, katalog_version: job.katalog && job.katalog.version,
      erstellt_am: $now.toISO() }, folien },
    bloecke: bl.map((b, i) => ({ block: (zeilen[i] || {}).Block, titel: (zeilen[i] || {}).Titel,
      folien: ((b && b.folien) || []).length, qa: (b && b.qa) || { status: 'FEHLER', befunde: [] },
      quellen: (b && b.quellen) || [], fehler: (b && b.error) || '' })),
    konfig: job.konfig
  };
})() }}"""

exec(compile((Path(__file__).parent / "wf_new.py").read_text(encoding="utf-8"), "wf_new.py", "exec"))


if __name__ == "__main__":
    for f in (build_wf0, build_wf1, build_wf2, build_wf3, build_wf4, build_wf5, build_wf6, build_wf7, build_wf8,
              build_wf9, build_wf10):
        f()
    print("Workflows geschrieben nach", OUT)
