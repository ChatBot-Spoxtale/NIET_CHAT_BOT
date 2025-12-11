// src/embeddings/indexer.js
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const yaml = require("js-yaml");

const { embeddingModel } = require("../Config/geminiGenerate.js");
const { setDocuments } = require("../Vector/memoryStore.js");

const DATA_DIR = path.join(__dirname, "..", "Datas"); 
const CACHE_DIR = path.join(__dirname, "..", "cache");
const CACHE_FILE = path.join(CACHE_DIR, "embeddings.json");

const CONCURRENCY = 2;      
const MAX_RETRIES = 5;
const BASE_DELAY = 500;
const MAX_DELAY = 8000;
const EXTRA_THROTTLE_MS = 50; 

function createLimit(concurrency = 2) {``
  let active = 0;
  const queue = [];

  function runNext() {
    if (active >= concurrency || queue.length === 0) return;
    active++;
    const { fn, resolve, reject } = queue.shift();
    Promise.resolve()
      .then(fn)
      .then(resolve)
      .catch(reject)
      .finally(() => {
        active--;
        runNext();
      });
  }

  return function limit(fn) {
    return new Promise((resolve, reject) => {
      queue.push({ fn, resolve, reject });
      runNext();
    });
  };
}
const limit = createLimit(CONCURRENCY);

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function backoffDelay(attempt) {
  const exp = Math.min(MAX_DELAY, BASE_DELAY * Math.pow(2, attempt));
  return Math.floor(exp * (0.5 + Math.random() * 0.5));
}

function ensureCacheDir() {
  if (!fs.existsSync(CACHE_DIR)) fs.mkdirSync(CACHE_DIR, { recursive: true });
}

function loadCache() {
  ensureCacheDir();
  if (!fs.existsSync(CACHE_FILE)) return {};
  try {
    return JSON.parse(fs.readFileSync(CACHE_FILE, "utf8") || "{}");
  } catch (e) {
    console.warn("Warning: failed to parse cache, starting fresh:", e.message);
    return {};
  }
}

function saveCacheAtomic(cacheObj) {
  ensureCacheDir();
  const tmp = CACHE_FILE + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(cacheObj), "utf8");
  fs.renameSync(tmp, CACHE_FILE);
}

function hashText(text) {
  return crypto.createHash("sha256").update(text, "utf8").digest("hex");
}

const embeddingCache = loadCache();

async function createEmbeddingApiCall(text) {
  const res = await embeddingModel.embedContent(text);
  return res.embedding.values;
}

async function safeCreateEmbeddingWithCache(text) {
  const key = hashText(text);
  if (embeddingCache[key] && Array.isArray(embeddingCache[key].embedding)) {
    return embeddingCache[key].embedding;
  }

  return limit(async () => {
    let lastErr = null;
    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      try {
        if (EXTRA_THROTTLE_MS > 0 && attempt === 0) await sleep(EXTRA_THROTTLE_MS);

        const emb = await createEmbeddingApiCall(text);

        embeddingCache[key] = {
          embedding: emb,
          textHash: key,
          textLength: text.length,
          createdAt: new Date().toISOString()
        };

        try { saveCacheAtomic(embeddingCache); } catch (e) { console.warn("Warning: cache save failed:", e.message); }

        return emb;
      } catch (err) {
        lastErr = err;
        const status = err?.status || err?.code || null;

        if (status >= 400 && status < 500 && status !== 429) {
          throw err;
        }

        if (attempt === MAX_RETRIES) break;

        const wait = backoffDelay(attempt);
        console.warn(`Embedding attempt ${attempt + 1} failed; retrying in ${wait}ms. Error:`, err?.message || err);
        await sleep(wait);
      }
    }
    throw lastErr;
  });
}

function getAllFilesRecursively(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  let files = [];
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) files = files.concat(getAllFilesRecursively(full));
    else files.push(full);
  }
  return files;
}

function parseToon(content, filename = "unknown.toon") {
  const lines = content.split(/\r?\n/);
  const docs = [];
  let current = null;

  function pushCurrent() {
    if (!current) return;
    const parts = [];
    if (current.header) parts.push(current.header);
    for (const [k, v] of Object.entries(current.fields || {})) {
      if (Array.isArray(v)) parts.push(`${k}: ${v.join("\n")}`);
      else parts.push(`${k}: ${v}`);
    }
    const text = parts.join("\n").trim();
    if (text) {
      docs.push({ id: `${filename}::${docs.length+1}`, key: current.header || "toon_block", text, metadata: { source: filename }});
    }
    current = null;
  }

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;
    const headerMatch = line.match(/^\[(.+?)\]$/);
    if (headerMatch) { pushCurrent(); current = { header: headerMatch[1], fields: {} }; continue; }
    const kv = line.match(/^([^:]+):\s*(.+)$/);
    if (kv && current) {
      const k = kv[1].trim(), v = kv[2].trim();
      if (current.fields[k]) {
        if (Array.isArray(current.fields[k])) current.fields[k].push(v);
        else current.fields[k] = [current.fields[k], v];
      } else current.fields[k] = v;
      continue;
    }
    if (current) current.fields.content = (current.fields.content || "") + "\n" + line;
  }
  pushCurrent();
  if (docs.length === 0) {
    docs.push({ id: `${filename}::1`, key: path.basename(filename, ".toon"), text: content, metadata: { source: filename, fallback: true }});
  }
  return docs;
}

function flattenYamlToDocs(topKey, obj, filename) {
  const docs = [];
  function walk(prefix, node) {
    if (typeof node === "string") { docs.push({ key: prefix || topKey, text: node, metadata: { source: filename } }); return; }
    if (Array.isArray(node)) { docs.push({ key: prefix || topKey, text: node.join("\n"), metadata: { source: filename } }); return; }
    if (typeof node === "object" && node !== null) {
      const keys = Object.keys(node);
      const numeric = keys.length > 0 && keys.every(k => /^\d+$/.test(k));
      if (numeric) {
        const text = keys.sort((a,b)=>Number(a)-Number(b)).map(k=>node[k]).join("\n");
        docs.push({ key: prefix || topKey, text, metadata: { source: filename }});
        return;
      }
      for (const [k,v] of Object.entries(node)) walk(prefix ? `${prefix}.${k}` : k, v);
    }
  }
  walk("", obj);
  return docs;
}

async function buildIndex() {
  if (!fs.existsSync(DATA_DIR)) { console.error("Data folder not found:", DATA_DIR); return; }

  const filePaths = getAllFilesRecursively(DATA_DIR);
  const docs = [];
  let idCounter = 1;

  console.log(`Found ${filePaths.length} files under ${DATA_DIR}. Cached embeddings: ${Object.keys(embeddingCache).length}`);

  for (const fullPath of filePaths) {
    const fileName = path.basename(fullPath);
    const ext = path.extname(fileName).toLowerCase();
    if (fileName.startsWith(".")) continue;

    let raw;
    try { raw = fs.readFileSync(fullPath, "utf8"); } catch (e) { console.warn("Failed to read", fullPath, e.message); continue; }

    try {
      if (ext === ".json") {
        const kb = JSON.parse(raw);
        for (const [key, section] of Object.entries(kb)) {
          const text =
            (section.overview ? section.overview + "\n" : "") +
            (section.details ? section.details + "\n" : "") +
            (Array.isArray(section.points) ? section.points.join("\n") + "\n" : "");
          const normalized = text.trim() || JSON.stringify(section);
          const emb = await safeCreateEmbeddingWithCache(normalized);
          docs.push({ id: idCounter++, key: `${fileName}:${key}`, text: normalized, metadata: { source: fileName, section: key }});
        }
      } else if (ext === ".toon") {
        let parsedYaml = null;
        try { parsedYaml = yaml.load(raw); } catch (e) { parsedYaml = null; }

        if (parsedYaml && typeof parsedYaml === "object") {
          const blocks = flattenYamlToDocs(fileName, parsedYaml, fileName);
          for (const b of blocks) {
            const text = b.text.trim();
            const emb = await safeCreateEmbeddingWithCache(text);
            docs.push({ id: idCounter++, key: `${fileName}:${b.key}`, text, metadata: { source: fileName }});
          }
        } else {
          const blocks = parseToon(raw, fileName);
          for (const b of blocks) {
            const text = b.text.trim();
            const emb = await safeCreateEmbeddingWithCache(text);
            docs.push({ id: idCounter++, key: `${fileName}:${b.key}`, text, metadata: { source: fileName }});
          }
        }
      } else if (ext === ".txt" || ext === ".md") {
        const text = raw.trim();
        const emb = await safeCreateEmbeddingWithCache(text);
        docs.push({ id: idCounter++, key: fileName, text, metadata: { source: fileName }});
      } else {
        continue;
      }
    } catch (err) {
      console.error("Error processing file:", fullPath, err?.message || err);
    }
  }

  setDocuments(docs);
  console.log(`Indexing complete — documents: ${docs.length}. Cache size: ${Object.keys(embeddingCache).length}`);
}

ensureCacheDir();
function initEmbeddingCache() {
  return;
}
initEmbeddingCache();

process.on("exit", () => { try { saveCacheAtomic(embeddingCache); } catch (e) {} });
process.on("SIGINT", () => { try { saveCacheAtomic(embeddingCache); } catch (e) {}; process.exit(0); });

if (require.main === module) {
  buildIndex().catch(err => { console.error("Indexer error:", err?.message || err); process.exit(1); });
}

module.exports = { buildIndex };
