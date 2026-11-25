// Führt ECOMEX-Workflows mit der echten n8n-2.46-Engine (n8n-core WorkflowExecute + n8n-nodes-base) aus.
// Externe Dienste werden mit nock simuliert, der Renderer läuft echt (lokal). KI-Bausteine werden gefälscht.
require('./stub.js');
const path = require('path');
const fs = require('fs');
const { Container } = require('@n8n/di');
const core = require('n8n-core');
const { Workflow, NodeHelpers, createRunExecutionData } = require('n8n-workflow');

const WF_DIR = process.env.WF_DIR || path.resolve(__dirname, '../../../workflows');

// ------------------------------------------------------------------ Node-Typen
const index = {};
const byFile = {};
function walk(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.name.endsWith('.node.js')) { byFile[e.name.replace(/\.node\.js$/, '').toLowerCase()] = byFile[e.name.replace(/\.node\.js$/, '').toLowerCase()] || p; }
    else if (e.name.endsWith('.node.json')) {
      try { const j = JSON.parse(fs.readFileSync(p, 'utf8')); if (j.node) out[j.node] = p.replace(/\.node\.json$/, '.node.js'); } catch (err) { }
    }
  }
}
walk(path.join(__dirname, 'node_modules/n8n-nodes-base/dist/nodes'), index);
walk(path.join(__dirname, 'node_modules/@n8n/n8n-nodes-langchain/dist/nodes'), index);
index['@n8n/n8n-nodes-langchain.anthropic'] = path.join(__dirname, 'node_modules/@n8n/n8n-nodes-langchain/dist/nodes/vendors/Anthropic/Anthropic.node.js');

const cache = {};
function loadReal(type) {
  if (cache[type]) return cache[type];
  const file = (index[type] && fs.existsSync(index[type])) ? index[type] : byFile[type.split('.').pop().toLowerCase()];
  if (!file || !fs.existsSync(file)) throw new Error('Node-Typ nicht gefunden: ' + type);
  const mod = require(file);
  const C = Object.values(mod).find(v => typeof v === 'function' && /Node|Trigger|^[A-Z]/.test(v.name));
  return (cache[type] = new C());
}

// Fälschungen: echte Beschreibung (Parameter!), eigene execute()-Funktion
const FAKES = {};
function fake(type, exec) { FAKES[type] = exec; }

function makeNodeTypes() {
  const get = (type, version) => {
    const real = loadReal(type);
    const v = NodeHelpers.getVersionedNodeType(real, version);
    if (!FAKES[type]) return v;
    const f = Object.create(v);
    f.description = v.description;
    f.execute = async function (ctx) { return FAKES[type].call(ctx && ctx.getNodeParameter ? ctx : this); };
    f.webhook = undefined; f.trigger = undefined; f.poll = undefined; f.supplyData = undefined;
    return f;
  };
  return { getByName: t => loadReal(t), getByNameAndVersion: get, getKnownTypes: () => ({}) };
}

const passthrough = async function () { return [this.getInputData()]; };
for (const t of ['n8n-nodes-base.formTrigger', 'n8n-nodes-base.manualTrigger', 'n8n-nodes-base.scheduleTrigger',
  'n8n-nodes-base.executeWorkflowTrigger']) fake(t, passthrough);

// Form-Abschluss: wertet die Meldung aus und prüft, ob die zurückgegebene Datei existiert
fake('n8n-nodes-base.form', async function () {
  const op = this.getNodeParameter('operation', 0, 'page');
  const items = this.getInputData();
  if (op === 'completion') {
    const respondWith = this.getNodeParameter('respondWith', 0, 'text');
    const out = { formular: 'abschluss', respondWith, titel: this.getNodeParameter('completionTitle', 0, ''), meldung: this.getNodeParameter('completionMessage', 0, '') };
    if (respondWith === 'returnBinary') {
      const prop = this.getNodeParameter('inputDataFieldName', 0, 'data');
      const bin = items[0].binary && items[0].binary[prop];
      if (!bin) throw new Error('Form: Binärfeld „' + prop + '“ fehlt – nichts zum Herunterladen');
      out.datei = bin.fileName; out.bytes = bin.fileSize;
    }
    return [[{ json: out, binary: items[0].binary }]];
  }
  const antwort = (global.FORM_ANTWORTEN || {})[this.getNode().name] || {};
  return [[{ json: { ...antwort } }]];
});

// KI-Bausteine
fake('@n8n/n8n-nodes-langchain.chainLlm', async function () {
  const key = (this.getWorkflow().name || this.getWorkflow().id) + '/' + this.getNode().name;
  // Prompt-Ausdrücke wirklich auswerten: kaputte Node-Verweise würden hier auffallen
  const prompt = this.getNodeParameter('text', 0, '');
  const sys = this.getNodeParameter('messages.messageValues', 0, []);
  global.PROMPTS = global.PROMPTS || {};
  global.PROMPTS[key] = { prompt: String(prompt), system: (sys || []).map(m => String(m.message || '')).join('\n') };
  const f = (global.LLM_ANTWORTEN || {})[key];
  if (f && f.__fehler) throw new Error(f.__fehler);
  return [this.getInputData().map(() => ({ json: f || { text: 'OK' } }))];
});
fake('@n8n/n8n-nodes-langchain.anthropic', async function () {
  const prop = this.getNodeParameter('binaryPropertyName', 0, 'data');
  const it = this.getInputData()[0];
  if (!it.binary || !it.binary[prop]) throw new Error('Analyze document: Binärfeld ' + prop + ' fehlt');
  return [[{ json: { content: [{ type: 'text', text: 'GESAMT: OK\n| Folie | Problem | Vorschlag |\n|---|---|---|\nFolien wirken ruhig.' }] } }]];
});
fake('@n8n/n8n-nodes-langchain.vectorStoreSupabase', async function () {
  const mode = this.getNodeParameter('mode', 0);
  const items = this.getInputData();
  global.VS_LOG = global.VS_LOG || [];
  if (mode === 'insert') {
    global.VS_LOG.push({ wf: this.getWorkflow().name, items: items.map(i => i.json) });
    return [items.map(i => ({ json: { pageContent: String(i.json.content || ''), metadata: { locator: i.json.locator } } }))];
  }
  global.VS_LOG.push({ wf: this.getWorkflow().name, load: this.getNodeParameter('prompt', 0), filter: this.getNodeParameter('options', 0) });
  return [[{ json: { document: { pageContent: 'Interner Treffer', metadata: { title: 'Bitkom Leitfaden', locator: 'Seite 3' } }, score: 0.81 } }]];
});

// ------------------------------------------------------------------ Credentials (gefälscht)
const HEADER = {
  renderer: { name: 'X-API-Key', value: 'testkey' },
  anthropic: { name: 'x-api-key', value: 'sk-ant-test' },
  azure: { name: 'Ocp-Apim-Subscription-Key', value: 'az-test' },
};
const credentialsHelper = {
  async getDecrypted(_ad, nodeCredentials, type) {
    if (type === 'httpHeaderAuth') return HEADER[nodeCredentials.id];
    if (type === 'supabaseApi') return { host: 'https://test.supabase.co', serviceRole: 'sb-secret-test' };
    if (type === 'githubApi') return { server: 'https://api.github.com', user: 'x', accessToken: 'gh-test' };
    return { apiKey: 'test' };
  },
  async authenticate(creds, type, opts) {
    opts.headers = opts.headers || {};
    if (type === 'supabaseApi') { opts.headers.apikey = creds.serviceRole; opts.headers.Authorization = 'Bearer ' + creds.serviceRole; }
    if (type === 'githubApi') opts.headers.Authorization = 'token ' + creds.accessToken;
    return opts;
  },
  async preAuthentication() { return undefined; },
  async runPreAuthentication() { return undefined; },
  isCredentialUsableByNode() { return true; },
  getParentTypes() { return []; },
  getCredentialsProperties() { return []; },
  async updateCredentials() { },
  async updateCredentialsOauthTokenData() { },
};

function patchCredentials(wf) {
  for (const n of wf.nodes) {
    const p = n.parameters || {};
    const note = n.notes || '';
    if (n.type === 'n8n-nodes-base.httpRequest' && p.authentication === 'genericCredentialType') {
      const id = /Renderer/.test(note) ? 'renderer' : /Azure/.test(note) ? 'azure' : /Anthropic/.test(note) ? 'anthropic' : null;
      if (!id) throw new Error('Header-Credential unklar: ' + wf.name + ' / ' + n.name);
      n.credentials = { httpHeaderAuth: { id, name: id } };
    }
    if (n.type === 'n8n-nodes-base.httpRequest' && p.nodeCredentialType === 'supabaseApi') n.credentials = { supabaseApi: { id: 'sb', name: 'sb' } };
    if (n.type === 'n8n-nodes-base.supabase') n.credentials = { supabaseApi: { id: 'sb', name: 'sb' } };
    if (n.type === 'n8n-nodes-base.github') n.credentials = { githubApi: { id: 'gh', name: 'gh' } };
    if (n.type === 'n8n-nodes-base.executeWorkflow') n.parameters.workflowId = { __rl: true, mode: 'id', value: n.parameters.workflowId.cachedResultName };
  }
}

// ------------------------------------------------------------------ Workflows laden
const WORKFLOWS = {};
for (const f of fs.readdirSync(WF_DIR).filter(f => f.endsWith('.json'))) {
  const wf = JSON.parse(fs.readFileSync(path.join(WF_DIR, f), 'utf8'));
  WORKFLOWS[wf.name] = wf;
}

let execCounter = 0;
const nodeTypes = makeNodeTypes();
let binaryReady = false;
async function initBinary() {
  if (binaryReady) return;
  const cfg = Container.get(core.BinaryDataConfig);
  cfg.mode = 'filesystem';
  cfg.localStoragePath = require('path').join(require('os').tmpdir(), 'ecomex-n8n-binary');
  require('fs').mkdirSync(cfg.localStoragePath, { recursive: true });
  await Container.get(core.BinaryDataService).init();
  binaryReady = true;
}

global.SUB_OVERRIDES = {};
global.SUB_CALLS = [];

function additionalDataFor(depth) {
  return {
    credentialsHelper,
    executeWorkflow: async (workflowInfo, _ad, options) => {
      const name = workflowInfo.id;
      global.SUB_CALLS.push({ name, items: (options.inputData || []).length, wait: !options.doNotWaitToFinish });
      if (global.SUB_OVERRIDES[name]) {
        return { executionId: 'sub-' + (++execCounter), data: [global.SUB_OVERRIDES[name](options.inputData)], waitTill: undefined };
      }
      const run = await runWorkflow(name, options.inputData, { depth: depth + 1 });
      const rd = run.data.resultData;
      if (rd.error) throw rd.error;
      const last = rd.lastNodeExecuted;
      const runs = rd.runData[last];
      return { executionId: 'sub-' + (++execCounter), data: runs[runs.length - 1].data.main, waitTill: undefined };
    },
    restApiUrl: 'http://localhost:5678/rest', instanceBaseUrl: 'http://localhost:5678/', webhookBaseUrl: 'http://localhost:5678/webhook',
    webhookWaitingBaseUrl: 'http://localhost:5678/webhook-waiting', webhookTestBaseUrl: 'http://localhost:5678/webhook-test',
    formWaitingBaseUrl: 'http://localhost:5678/form-waiting', currentNodeExecutionIndex: 0, variables: {}, userId: 'u1',
    setExecutionStatus: () => { }, sendDataToUI: () => { }, logAiEvent: () => { }, getRunExecutionData: async () => undefined,
  };
}

async function runWorkflow(name, items, opts = {}) {
  await initBinary();
  const src = WORKFLOWS[name];
  if (!src) throw new Error('Workflow fehlt: ' + name);
  const wfJson = JSON.parse(JSON.stringify(src));
  if (opts.patch) opts.patch(wfJson);
  if (global.KONFIG_PATCH && wfJson.name.startsWith('ECOMEX 0 |')) global.KONFIG_PATCH(wfJson);
  patchCredentials(wfJson);
  const workflow = new Workflow({ id: name, name, nodes: wfJson.nodes, connections: wfJson.connections, active: false,
    nodeTypes, settings: wfJson.settings, staticData: {} });
  const triggerTypes = ['n8n-nodes-base.formTrigger', 'n8n-nodes-base.manualTrigger', 'n8n-nodes-base.executeWorkflowTrigger'];
  const start = wfJson.nodes.find(n => (opts.start ? n.name === opts.start : triggerTypes.includes(n.type)) && !n.disabled);
  const hooks = new core.ExecutionLifecycleHooks('manual', 'exec-' + (++execCounter), wfJson);
  const ad = additionalDataFor(opts.depth || 0);
  ad.hooks = hooks;
  const red = createRunExecutionData({ executionData: { nodeExecutionStack: [{ node: workflow.getNode(start.name), data: { main: [items] }, source: null }] } });
  const we = new core.WorkflowExecute(ad, 'manual', red);
  return await we.processRunExecutionData(workflow);
}

// Hilfen für Tests
async function binaryItem(json, prop, file, mimeType) {
  await initBinary();
  const buf = fs.readFileSync(file);
  const meta = await Container.get(core.BinaryDataService).store({ type: 'execution', workflowId: 'test', executionId: 'test' }, buf,
    { fileName: path.basename(file), mimeType, fileExtension: path.extname(file).slice(1), data: '' });
  return { json, binary: { [prop]: meta } };
}
function out(run, node, branch = 0, runIndex) {
  const r = run.data.resultData.runData[node];
  if (!r) return null;
  const x = r[runIndex === undefined ? r.length - 1 : runIndex];
  return x && x.data && x.data.main ? (x.data.main[branch] || []) : [];
}
function executed(run) { return Object.keys(run.data.resultData.runData); }

async function readBinary(b) { return await Container.get(core.BinaryDataService).getAsBuffer(b); }
module.exports = { runWorkflow, binaryItem, out, executed, WORKFLOWS, fake, readBinary };
