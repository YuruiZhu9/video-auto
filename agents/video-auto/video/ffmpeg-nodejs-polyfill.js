/**
 * Node.js FFmpeg WASM 兼容层
 * 为 @ffmpeg/ffmpeg 在 Node.js 22+ 环境下提供 Worker 和 Web API polyfill
 * 
 * 用法：在加载 @ffmpeg/ffmpeg 之前，先加载此文件
 *   require('./node-polyfill.js')
 *   const { FFmpeg } = require('@ffmpeg/ffmpeg')
 *
 * 或者在 ESM 中：
 *   import './node-polyfill.js'
 *   import { FFmpeg } from '@ffmpeg/ffmpeg'
 */

const { Worker, MessageChannel, parentPort } = require('worker_threads');

// ── 全局 Web API Polyfill ──────────────────────────────────────

if (typeof globalThis.location === 'undefined') {
  Object.defineProperty(globalThis, 'location', {
    value: new URL('file:///'),
    writable: false,
    configurable: false,
  });
}

if (typeof globalThis.navigator === 'undefined') {
  Object.defineProperty(globalThis, 'navigator', {
    value: { userAgent: 'node.js' },
    writable: true,
    configurable: false,
  });
}

if (typeof globalThis.crypto === 'undefined') {
  // Node.js crypto for randomUUID etc.
  const { randomUUID, webcrypto } = require('crypto');
  Object.defineProperty(globalThis, 'crypto', {
    value: { randomUUID, ...webcrypto },
    writable: true,
    configurable: false,
  });
}

if (typeof globalThis.fetch === 'undefined') {
  // Node.js 22 has native fetch
  globalThis.fetch = (...args) => import('node-fetch').then(m => m.default(...args));
}

// ── Blob / File / URL Polyfill ──────────────────────────────────

class NodeBlob {
  constructor(parts, options = {}) {
    this._parts = parts.map(p =>
      p instanceof Uint8Array ? p
      : typeof p === 'string' ? Buffer.from(p)
      : Buffer.from(JSON.stringify(p))
    );
    this.type = options.type || '';
    this.size = this._parts.reduce((a, b) => a + b.length, 0);
  }
  arrayBuffer() { return Promise.resolve(Buffer.concat(this._parts)); }
  text() { return Promise.resolve(Buffer.concat(this._parts).toString()); }
  slice() { return new NodeBlob([], {}); }
  stream() { return require('stream').Readable.from(Buffer.concat(this._parts)); }
}

class NodeFile extends NodeBlob {
  constructor(bits, name, options = {}) {
    super(bits, options);
    this.name = name;
    this.lastModified = Date.now();
  }
}

globalThis.Blob = NodeBlob;
globalThis.File = NodeFile;

globalThis.URL = class {
  constructor(url, base) {
    if (url.startsWith('data:')) {
      const parts = url.split(',');
      this.href = url;
      this.protocol = 'data:';
      this.pathname = parts[0];
    } else if (base) {
      const b = new URL(base);
      if (url.startsWith('/')) {
        this.pathname = url;
        this.href = `${b.protocol}//localhost${url}`;
      } else {
        this.pathname = `${b.pathname.replace(/\/[^/]*$/, '')}/${url}`;
        this.href = `${b.protocol}//localhost${this.pathname}`;
      }
    } else {
      this.pathname = url;
      this.href = `file://${url}`;
    }
    this.pathname = this.href.replace('file://', '/');
  }
  static createObjectURL(blob) { return `blob:${blob.type || 'node'}`; }
  static revokeObjectURL() {}
};

globalThis.URL.createObjectURL = (blob) => `blob:${Date.now()}`;
globalThis.URL.revokeObjectURL = () => {};

// ── Worker Polyfill ─────────────────────────────────────────────
// 拦截 @ffmpeg/ffmpeg 中的 new Worker(new URL(...)) 调用
// 改用 node worker_threads.Worker

// Monkey-patch URL to handle worker blob URLs
const OriginalURL = globalThis.URL;
let _workerCode = null;

// 创建一个假的 Worker 类，返回一个 proxy Worker
globalThis.Worker = class Worker {
  constructor(url, options) {
    if (url instanceof URL) {
      this._url = url;
    } else {
      this._url = new URL(url, 'file:///');
    }
    this._worker = null;
    this._handlers = { message: [], error: [], close: [] };

    // 生成 worker 入口代码（注入 WASM 支持）
    const workerEntry = `
      const { parentPort } = require('worker_threads');
      const { readFileSync, readFile } = require('fs');
      const { fileURLToPath } = require('url');
      const path = require('path');

      // 模拟 postMessage / onmessage（通过 parentPort）
      self.postMessage = (type, data) => parentPort.postMessage({ type, data });
      self.on = (evt, cb) => {
        if (evt === 'message') parentPort.on('message', cb);
        if (evt === 'error') parentPort.on('error', cb);
      };
      self.close = () => parentPort.close?.();
      self.importScripts = () => {};
      self.location = { href: '${this._url.href}', origin: 'file://' };

      // 加载原始 worker 脚本
      const scriptPath = '${this._url.pathname}';
      if (scriptPath.endsWith('.js')) {
        try {
          const { pathToFileURL } = require('url');
          const fn = require(scriptPath);
        } catch(e) {
          // ignore
        }
      }
    `;

    try {
      this._worker = new Worker(workerEntry, {
        eval: true,
        stdio: ['pipe', 'pipe', 'pipe', 'ipc'],
      });
      this._worker.on('message', (msg) => {
        if (msg.type === 'ready') {
          this._handlers.message.forEach(h => h({ data: msg.data }));
        }
      });
      this._worker.on('error', (e) => {
        this._handlers.error.forEach(h => h(e));
      });
    } catch (e) {
      // Worker 创建失败，降级
    }
  }

  postMessage(data, transfer) {
    if (this._worker) {
      try {
        this._worker.postMessage(data, transfer);
      } catch {}
    }
  }

  onmessage(data) {
    this._handlers.message.push(data);
  }

  addEventListener(type, handler) {
    if (type === 'message') this._handlers.message.push(handler);
    if (type === 'error') this._handlers.error.push(handler);
  }

  terminate() {
    this._worker?.terminate?.();
  }
};

globalThis.Worker.prototype.onmessage = null;
globalThis.addEventListener = (evt, handler) => {
  if (evt === 'message') {
    if (!globalThis._msgHandlers) globalThis._msgHandlers = [];
    globalThis._msgHandlers.push(handler);
  }
};

// ── BroadcastChannel Polyfill ───────────────────────────────────
globalThis.BroadcastChannel = class {
  constructor(name) { this.name = name; this._handlers = []; }
  postMessage(msg) { this._handlers.forEach(h => h({ data: msg })); }
  addEventListener(type, h) { if (type === 'message') this._handlers.push(h); }
  close() {}
};

// ── MessageChannel Polyfill ─────────────────────────────────────
globalThis.MessageChannel = MessageChannel;

// ── EventTarget Polyfill ─────────────────────────────────────────
if (typeof globalThis.EventTarget === 'undefined') {
  globalThis.EventTarget = class {
    constructor() { this._handlers = {}; }
    addEventListener(type, handler) {
      (this._handlers[type] = this._handlers[type] || []).push(handler);
    }
    removeEventListener(type, handler) {
      if (this._handlers[type]) {
        this._handlers[type] = this._handlers[type].filter(h => h !== handler);
      }
    }
    dispatchEvent(event) {
      const handlers = this._handlers[event.type] || [];
      handlers.forEach(h => h.call(this, event));
      return true;
    }
  };
}

if (typeof globalThis.Event === 'undefined') {
  globalThis.Event = class Event {
    constructor(type, options = {}) {
      this.type = type;
      this.bubbles = !!options.bubbles;
      this.cancelable = !!options.cancelable;
      this.detail = options.detail;
    }
  };
}

// ── AbortController / Signal Polyfill ──────────────────────────
if (typeof globalThis.AbortController === 'undefined') {
  globalThis.AbortController = class {
    constructor() { this.signal = { aborted: false, reason: null }; }
    abort(reason) { this.signal.aborted = true; this.signal.reason = reason; }
  };
}

// ── TextEncoder / TextDecoder Polyfill ─────────────────────────
if (typeof globalThis.TextEncoder === 'undefined') {
  globalThis.TextEncoder = class {
    encode(s) { return Buffer.from(s); }
  };
}
if (typeof globalThis.TextDecoder === 'undefined') {
  globalThis.TextDecoder = class {
    decode(b) { return Buffer.from(b).toString(); }
  };
}

// ── 导出给外部使用 ─────────────────────────────────────────────
module.exports = {
  version: '1.0.0-nodejs',
  note: 'Run: require("@ffmpeg/ffmpeg") AFTER this polyfill',
};
