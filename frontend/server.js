import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

const port = Number.parseInt(process.env.PORT ?? "36300", 10);
if (!Number.isFinite(port)) {
  throw new Error("PORT must be a valid number");
}

const publicDir = path.join(__dirname, "public");
app.use(express.static(publicDir));

app.get("/health", (_req, res) => {
  res.json({ ok: true });
});

app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`Frontend listening on :${port}`);
});
