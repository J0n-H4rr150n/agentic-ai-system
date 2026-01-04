export function createId(prefix = "id") {
  const rnd = Math.random().toString(16).slice(2);
  const ts = Date.now().toString(16);
  return `${prefix}-${ts}-${rnd}`;
}
