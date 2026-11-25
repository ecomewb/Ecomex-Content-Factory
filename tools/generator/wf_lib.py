"""Kleine Hilfsbibliothek zum Erzeugen importierbarer n8n-Workflows (n8n 2.46)."""
import json
import uuid
from pathlib import Path

NS = uuid.UUID("6f1c2b1e-7c55-4d7e-9a0e-ec0e5c0f0001")


def _id(*parts):
    return str(uuid.uuid5(NS, "|".join(str(p) for p in parts)))


CRED_AUTO = {
    "n8n-nodes-base.github": "GitHub",
    "n8n-nodes-base.supabase": "Supabase",
    "@n8n/n8n-nodes-langchain.vectorStoreSupabase": "Supabase",
    "@n8n/n8n-nodes-langchain.lmChatAnthropic": "Anthropic (KI-Credential)",
    "@n8n/n8n-nodes-langchain.anthropic": "Anthropic (KI-Credential)",
    "@n8n/n8n-nodes-langchain.lmChatOpenAi": "OpenAI (KI-Credential)",
    "@n8n/n8n-nodes-langchain.embeddingsOpenAi": "OpenAI (KI-Credential)",
}


class WF:
    def __init__(self, name, tags=None):
        self.name = name
        self.nodes = []
        self.connections = {}
        self.tags = tags or []

    # ----------------------------------------------------------- Knoten
    def node(self, name, type_, version, params, pos, notes=None, **extra):
        if any(n["name"] == name for n in self.nodes):
            raise ValueError(f"Doppelter Node-Name: {name}")
        n = {"parameters": params, "id": _id(self.name, name), "name": name, "type": type_,
             "typeVersion": version, "position": list(pos)}
        if notes:
            n["notes"] = notes
            n["notesInFlow"] = True
        if type_ in ("n8n-nodes-base.formTrigger", "n8n-nodes-base.form", "n8n-nodes-base.wait"):
            n["webhookId"] = _id(self.name, name, "webhook")
        n.update(extra)
        self.nodes.append(n)
        return name

    def sticky(self, key, content, pos, w, h, color=None):
        p = {"content": content, "height": h, "width": w}
        if color:
            p["color"] = color
        self.nodes.append({"parameters": p, "id": _id(self.name, "sticky", key), "name": f"Sticky Note {key}",
                           "type": "n8n-nodes-base.stickyNote", "typeVersion": 1, "position": list(pos)})

    # ----------------------------------------------------------- Verbindungen
    def link(self, a, b, out=0, inp=0, kind="main"):
        c = self.connections.setdefault(a, {}).setdefault(kind, [])
        while len(c) <= out:
            c.append([])
        c[out].append({"node": b, "type": kind, "index": inp})

    def ai(self, sub, root, kind):
        self.link(sub, root, 0, 0, kind)

    def chain(self, *names):
        for a, b in zip(names, names[1:]):
            self.link(a, b)

    # ----------------------------------------------------------- Ausgabe
    def _annotate_credentials(self):
        """Hängt an jeden Node, der Zugangsdaten braucht, einen sichtbaren Hinweis (🔑 …) an die Notiz."""
        for n in self.nodes:
            label = n.pop("_cred", None)
            p = n.get("parameters", {})
            if label is None:
                if n["type"] == "n8n-nodes-base.httpRequest" and p.get("nodeCredentialType") == "supabaseApi":
                    label = "Supabase"
                else:
                    label = CRED_AUTO.get(n["type"])
            if not label or n.get("disabled"):
                continue
            hinweis = "🔑 " + label
            if hinweis not in n.get("notes", ""):
                n["notes"] = (n.get("notes", "") + "\n" + hinweis).strip()
                n["notesInFlow"] = True

    def to_json(self, settings=None):
        self._annotate_credentials()
        s = {"executionOrder": "v1", "binaryMode": "separate", "saveManualExecutions": True,
             "saveDataErrorExecution": "all", "saveDataSuccessExecution": "all", "callerPolicy": "workflowsFromSameOwner"}
        if settings:
            s.update(settings)
        return {"name": self.name, "nodes": self.nodes, "connections": self.connections, "pinData": {},
                "settings": s, "active": False, "meta": {"templateCredsSetupCompleted": False,
                                                          "ecomex_content_factory": "0.3"},
                "tags": []}

    def save(self, path, settings=None):
        Path(path).write_text(json.dumps(self.to_json(settings), ensure_ascii=False, indent=2), encoding="utf-8")


# ----------------------------------------------------------- Parameter-Bausteine
def assign(name, value, typ="string"):
    return {"id": _id("assign", name, value), "name": name, "value": value, "type": typ}


def set_params(assignments, include_other=False, options=None):
    p = {"assignments": {"assignments": assignments}}
    if include_other:
        p["includeOtherFields"] = True
    p["options"] = options or {}
    return p


def set_raw(expr, include_binary=True):
    return {"mode": "raw", "jsonOutput": expr, "options": {}}


def cond(left, op_type, operation, right=None, single=False):
    c = {"id": _id("cond", left, operation, right), "leftValue": left, "operator": {"type": op_type, "operation": operation}}
    if single:
        c["operator"]["singleValue"] = True
    else:
        c["rightValue"] = right
    return c


def filter_params(conds, combinator="and"):
    return {"conditions": {"options": {"caseSensitive": False, "leftValue": "", "typeValidation": "loose", "version": 2},
                           "conditions": conds, "combinator": combinator}, "looseTypeValidation": True, "options": {}}


def rl_list(value, name=None):
    d = {"__rl": True, "mode": "list", "value": value}
    if name:
        d["cachedResultName"] = name
    return d


def rl_name(expr):
    return {"__rl": True, "mode": "name", "value": expr}


def sub_wf(cached_name):
    return {"__rl": True, "mode": "list", "value": "", "cachedResultName": cached_name}


def form_field(label, name, ftype="text", required=False, **kw):
    f = {"fieldLabel": label, "fieldName": name}
    if ftype != "text":
        f["fieldType"] = ftype
    if required:
        f["requiredField"] = True
    f.update(kw)
    return f


def options(*opts):
    return {"values": [{"option": o} for o in opts]}
