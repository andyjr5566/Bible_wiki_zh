import { createServer } from 'node:http';
import { readFileSync, statSync } from 'node:fs';
import { resolve, extname, relative, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gzipSync } from 'node:zlib';

const defaultRoot = fileURLToPath(new URL('../dist/', import.meta.url));
const mime = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.mp3': 'audio/mpeg', '.glb': 'model/gltf-binary', '.svg': 'image/svg+xml' };

export async function serveDist(root = defaultRoot) {
  root = resolve(root);
  const server = createServer((req, res) => {
    try {
      const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      if (pathname === '/favicon.ico') { res.writeHead(204).end(); return; }
      let path = resolve(root, '.' + pathname);
      const inside = relative(root, path);
      if (inside.startsWith('..') || isAbsolute(inside)) { res.writeHead(403).end(); return; }
      if (statSync(path).isDirectory()) path = resolve(path, 'index.html');
      let body = readFileSync(path);
      const type = mime[extname(path)] || 'application/octet-stream';
      const headers = { 'Content-Type': type, 'Cache-Control': path.includes('assets') ? 'public, max-age=31536000, immutable' : 'no-cache', Vary: 'Accept-Encoding' };
      if (/\b(text\/|application\/json|image\/svg)/.test(type) && /gzip/.test(req.headers['accept-encoding'] || '')) {
        body = gzipSync(body); headers['Content-Encoding'] = 'gzip';
      }
      headers['Content-Length'] = body.length;
      res.writeHead(200, headers).end(body);
    } catch { res.writeHead(404).end(); }
  });
  await new Promise((done, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', done); });
  server.unref();
  return { server, url: `http://127.0.0.1:${server.address().port}/` };
}

// 各截圖工具預設自啟本站 dist 伺服器；可指向 preview 或部署後子路徑。
export const siteUrl = process.env.JOS_URL || (await serveDist()).url;
