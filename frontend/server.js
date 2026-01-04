import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

const backendUrl = process.env.BACKEND_URL;
if (!backendUrl) {
  throw new Error("BACKEND_URL environment variable required");
}

const port = Number.parseInt(process.env.PORT ?? "36300", 10);
if (!Number.isFinite(port)) {
  throw new Error("PORT must be a valid number");
}

const publicDir = path.join(__dirname, "public");
app.use(express.static(publicDir));

app.use("/api", async (req, res) => {
  const targetUrl = new URL(req.originalUrl, backendUrl);

  const headers = new Headers();
  for (const [key, value] of Object.entries(req.headers)) {
    if (value === undefined) {
      continue;
    }
    if (Array.isArray(value)) {
      headers.set(key, value.join(","));
      continue;
    }
    headers.set(key, value);
  }

  // Ensure Host/Origin reflect the upstream.
  headers.delete("host");

  let body;
  if (req.method !== "GET" && req.method !== "HEAD") {
    const chunks = [];
    for await (const chunk of req) {
      chunks.push(chunk);
    }
    body = Buffer.concat(chunks);
  }

  const upstream = await fetch(targetUrl, {
    method: req.method,
    headers,
    body,
  });

  res.status(upstream.status);

  upstream.headers.forEach((value, key) => {
    // Some headers should be set by Node/Express.
    if (key.toLowerCase() === "content-encoding") {
      return;
    }
    res.setHeader(key, value);
  });

  const buffer = Buffer.from(await upstream.arrayBuffer());
  res.send(buffer);
});

app.get("/health", (_req, res) => {
  res.json({ ok: true });
});

app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`Frontend listening on :${port}`);
});
