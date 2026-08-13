#!/usr/bin/env node
/**
 * figma-mcp-go MCP stdio client (minimal, dependency-free).
 * Spawns the bridge server, performs the MCP handshake, and exposes
 * request() so any agent can call the 73 bridge tools over JSON-RPC.
 *
 * Usage (as a library):
 *   const { connect } = require("./mcp-client.js");
 *   const mcp = await connect({ port: 1994, waitForPlugin: true });
 *   const res = await mcp.call("get_selection", {});
 *   const res = await mcp.call("scan_text_nodes", { nodeId: "851:7" });
 *   await mcp.close();
 *
 * Notes:
 * - The bridge allows exactly ONE Figma plugin WebSocket connection.
 *   If a stale server holds port 1994, kill it first (the plugin
 *   auto-reconnects within ~1.5-2s once the new server is up).
 * - Every tool result is JSON text inside content[0].text — parse it.
 * - Call close() or the spawned server keeps running.
 */
const { spawn } = require("child_process");
const readline = require("readline");
const path = require("path");

function connect({ port = 1994, binary, waitForPlugin = false, timeoutMs = 20000 } = {}) {
  return new Promise(async (resolve, reject) => {
    // Resolve the bridge binary: explicit > ./vendor/ > $HOME/.figma-mcp-go/figma-mcp-go
    const candidates = [
      binary,
      path.join(__dirname, "..", "vendor", "figma-mcp-go"),
      path.join(process.env.HOME || "", ".figma-mcp-go", "figma-mcp-go"),
    ].filter(Boolean);
    let SERVER = null;
    for (const c of candidates) {
      try { if (require("fs").statSync(c).isFile()) { SERVER = c; break; } } catch {}
    }
    if (!SERVER) {
      return reject(new Error(
        "figma-mcp-go binary not found. Install it:\n" +
        "  npx -y @vkhanhqui/figma-mcp-go@latest\n" +
        "then symlink the binary into skills/figma-mcp/vendor/figma-mcp-go\n" +
        "or pass the `binary` option."
      ));
    }
    let proc;
    try {
      proc = spawn(SERVER, ["-ip", "127.0.0.1", "-port", String(port)], {
        stdio: ["pipe", "pipe", "ignore"],
      });
    } catch (e) { return reject(e); }

    const rl = readline.createInterface({ input: proc.stdout });
    let nextId = 1;
    const pending = new Map();

    function send(obj) { proc.stdin.write(JSON.stringify(obj) + "\n"); }
    function request(method, params = {}) {
      return new Promise((res, rej) => {
        const id = nextId++;
        pending.set(id, { resolve: res, reject: rej });
        send({ jsonrpc: "2.0", id, method, params });
      });
    }
    rl.on("line", (line) => {
      line = line.trim();
      if (!line) return;
      let msg;
      try { msg = JSON.parse(line); } catch { return; } // non-JSON log line
      if (msg.id && pending.has(msg.id)) {
        const p = pending.get(msg.id);
        pending.delete(msg.id);
        msg.error ? p.reject(new Error(JSON.stringify(msg.error))) : p.resolve(msg.result);
      }
    });

    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    const textOf = (r) => (r.content && r.content[0] && r.content[0].text) || "";

    try {
      await request("initialize", {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: { name: "figma-mcp-client", version: "1.0" },
      });
      send({ jsonrpc: "2.0", method: "notifications/initialized" });

      if (waitForPlugin) {
        const deadline = Date.now() + timeoutMs;
        let ready = false;
        while (Date.now() < deadline) {
          await sleep(1500);
          try {
            const r = await request("tools/call", { name: "get_selection", arguments: {} });
            if (textOf(r) && !textOf(r).includes("plugin not connected")) { ready = true; break; }
          } catch {}
        }
        if (!ready) { proc.kill(); return reject(new Error("Figma plugin did not reconnect")); }
      }

      resolve({
        proc,
        request,
        call: async (name, args = {}) => {
          const r = await request("tools/call", { name, arguments: args });
          return textOf(r);
        },
        callJson: async (name, args = {}) => {
          const t = textOf(await request("tools/call", { name, arguments: args }));
          try { return JSON.parse(t); } catch { return t; }
        },
        textOf,
        close: () => { try { proc.kill(); } catch {} },
      });
    } catch (e) {
      try { proc.kill(); } catch {}
      reject(e);
    }
  });
}

module.exports = { connect };
if (require.main === module) {
  // CLI smoke test: node mcp-client.js [port] [tool] [jsonArgs]
  // Full output by default; cap with CLI_CAP=2000 if you need bounded output.
  (async () => {
    const port = Number(process.argv[2] || 1994);
    const tool = process.argv[3] || "get_selection";
    const args = process.argv[4] ? JSON.parse(process.argv[4]) : {};
    const mcp = await connect({ port, waitForPlugin: true });
    const out = await mcp.call(tool, args);
    const cap = Number(process.env.CLI_CAP || 0);
    console.log(cap > 0 ? out.slice(0, cap) : out);
    mcp.close();
  })().catch((e) => { console.error("FAIL:", e.message); process.exit(1); });
}
