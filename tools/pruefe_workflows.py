#!/usr/bin/env python3
"""Prüft ECOMEX-n8n-Workflows (Export-JSON) auf typische Fehler nach Änderungen in n8n.

Aufruf:   python3 tools/pruefe_workflows.py workflows/*.json
          python3 tools/pruefe_workflows.py ~/Downloads/*.json      (nach Export aus n8n)

Geprüft wird ohne n8n und ohne Internet:
  FEHLER   Ausdrücke verweisen auf Nodes, die es im Workflow nicht (mehr) gibt   → $('Name') nach Umbenennen
  FEHLER   {{ und }} sind in einem Ausdruck nicht ausgeglichen
  FEHLER   Pflicht-Einstellungen in ECOMEX 0 fehlen (renderer_url, supabase_url, …)
  FEHLER   Ein Unterworkflow liefert sein Ergebnis nicht mehr über den vereinbarten End-Node
  HINWEIS  Call-Nodes ohne ausgewählten Unterworkflow (nach dem Import einmal auswählen)
  HINWEIS  Nodes ohne Zugangsdaten (Credentials), die welche brauchen
  HINWEIS  deaktivierte Nodes
Rückgabe: Exit-Code 1, wenn es FEHLER gibt.
"""
import json
import re
import sys
from pathlib import Path

REF = re.compile(r"""\$\(\s*(['"])((?:\\.|(?!\1).)+)\1\s*\)|\$node\[\s*(['"])((?:\\.|(?!\3).)+)\3\s*\]""")

# Einstellungen, auf die sich die anderen Workflows verlassen (ECOMEX 0 › Edit Fields)
KONFIG_PFLICHT = ["github_owner", "github_repo", "branch", "regel_ordner", "katalog_pfad", "renderer_url",
                  "supabase_url", "supabase_bucket", "wissensbasis_referenzen", "pptx_ohne_renderer",
                  "claude_pptx_modell", "claude_master_file_id", "anthropic_version", "code_execution_tool"]

# Unterworkflows: Ergebnis kommt aus dem zuletzt ausgeführten Node → dieser End-Node muss bleiben
END_NODES = {
    "ECOMEX 0": ["No Operation, do nothing", "No Operation, do nothing1"],
    "ECOMEX 7": ["No Operation, do nothing"],
    "ECOMEX 8": ["No Operation, do nothing"],
}

CRED_TYPES = {
    "n8n-nodes-base.github", "n8n-nodes-base.supabase", "n8n-nodes-base.microsoftSharePoint",
    "n8n-nodes-base.emailSend", "@n8n/n8n-nodes-langchain.lmChatAnthropic", "@n8n/n8n-nodes-langchain.lmChatOpenAi",
    "@n8n/n8n-nodes-langchain.embeddingsOpenAi", "@n8n/n8n-nodes-langchain.vectorStoreSupabase",
    "@n8n/n8n-nodes-langchain.anthropic",
}


def strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)
    elif isinstance(obj, str):
        yield obj


def pruefe(path):
    fehler, hinweise = [], []
    wf = json.loads(Path(path).read_text(encoding="utf-8"))
    name = wf.get("name", Path(path).stem)
    nodes = {n["name"]: n for n in wf.get("nodes", [])}

    for n in nodes.values():
        for s in strings(n.get("parameters", {})):
            if not s.startswith("=") and "{{" not in s:
                continue
            if s.count("{{") != s.count("}}"):
                fehler.append(f"[{n['name']}] Ausdruck mit unausgeglichenen {{{{ }}}} ({s.count('{{')}× '{{{{', {s.count('}}')}× '}}}}')")
            for m in REF.finditer(s):
                ref = (m.group(2) or m.group(4)).replace("\\'", "'").replace('\\"', '"')
                if ref not in nodes:
                    fehler.append(f"[{n['name']}] verweist auf Node „{ref}“, den es nicht gibt (umbenannt/gelöscht?)")
        if n.get("disabled"):
            hinweise.append(f"[{n['name']}] ist deaktiviert")
        if n["type"] == "n8n-nodes-base.executeWorkflow":
            wid = n.get("parameters", {}).get("workflowId", {})
            if isinstance(wid, dict) and not wid.get("value"):
                hinweise.append(f"[{n['name']}] Unterworkflow noch nicht ausgewählt (Liste „From list“ öffnen und "
                                f"„{wid.get('cachedResultName', '?')}“ wählen)")
        auth = n.get("parameters", {}).get("authentication")
        braucht = n["type"] in CRED_TYPES or (n["type"] == "n8n-nodes-base.httpRequest" and auth not in (None, "none"))
        if braucht and not n.get("credentials") and not n.get("disabled"):
            hinweise.append(f"[{n['name']}] Zugangsdaten (Credential) noch nicht gesetzt")

    # Verbindungen auf vorhandene Nodes
    for quelle, ausg in wf.get("connections", {}).items():
        if quelle not in nodes:
            fehler.append(f"Verbindung von „{quelle}“, den es nicht gibt")
        for art in ausg.values():
            for zweig in art:
                for z in zweig or []:
                    if z["node"] not in nodes:
                        fehler.append(f"Verbindung von „{quelle}“ zu „{z['node']}“, den es nicht gibt")

    # Verträge
    kurz = " ".join(name.split()[:2])
    if kurz == "ECOMEX 0":
        konf = None
        for n in nodes.values():
            if n["type"] == "n8n-nodes-base.set":
                namen = [a["name"] for a in n["parameters"].get("assignments", {}).get("assignments", [])]
                if "renderer_url" in namen:
                    konf = namen
        if konf is None:
            fehler.append("Einstellungs-Node (Edit Fields mit renderer_url) nicht gefunden")
        else:
            fehlend = [k for k in KONFIG_PFLICHT if k not in konf]
            if fehlend:
                fehler.append("Einstellungen fehlen in ECOMEX 0: " + ", ".join(fehlend))
    for ende in END_NODES.get(kurz, []):
        if ende not in nodes:
            fehler.append(f"End-Node „{ende}“ fehlt – der aufrufende Workflow bekommt sonst ein falsches Ergebnis")
    return name, list(dict.fromkeys(fehler)), list(dict.fromkeys(hinweise))


def main(argv):
    dateien = [a for a in argv if a.endswith(".json")]
    if not dateien:
        print(__doc__)
        return 2
    gesamt = 0
    for d in sorted(dateien):
        name, fehler, hinweise = pruefe(d)
        gesamt += len(fehler)
        status = "OK" if not fehler else f"{len(fehler)} FEHLER"
        print(f"\n=== {name}  ({Path(d).name}) – {status}")
        for f in fehler:
            print("  FEHLER  " + f)
        for h in hinweise:
            print("  Hinweis " + h)
    print(f"\n{gesamt} Fehler in {len(dateien)} Workflow(s).")
    return 1 if gesamt else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
