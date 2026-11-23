// Renders docs/REPRODUCTION.md from docs/demo-run.json (written by scripts/demo.mjs).
//
//   node scripts/reproduction.mjs

import { readFileSync, writeFileSync } from "fs";

const run = JSON.parse(readFileSync(new URL("../docs/demo-run.json", import.meta.url), "utf8"));
const EXPLORER = "https://explorer-studio.genlayer.com";
const tx = (h) => (h ? `[${h.slice(0, 10)}…](${EXPLORER}/tx/${h})` : "");
const esc = (s) => String(s ?? "").replace(/\|/g, "\\|");
const hashOf = (key) => {
  const [c, y] = key.split("-");
  return run.log.find((r) => r.call === `import_year("${c}", ${y})` && r.exec === "SUCCESS")?.hash;
};
const list = (a) => (a.length ? a.map((d) => `${d} ${esc(run.years[Object.keys(run.years).find((k) => run.years[k].names?.[d])]?.names?.[d] ?? "")}`.trim()).join("; ") : "—");

const rows = Object.entries(run.years).map(([key, y]) =>
  `| ${key} | **${y.status}** | ${y.nager.length} | ${y.openholidays.length} | ${list(y.nager_only)} | ${list(y.openholidays_only)} | \`${y.digest.slice(0, 16)}…\` | ${tx(hashOf(key))} |`);
const tables = Object.entries(run.years).filter(([, y]) => y.status === "AGREED").map(([key, y]) =>
  `- **${key}**: ${y.nager.map((d) => `${d} ${esc(y.names[d])}`).join(", ")}`);
const queries = run.queries.map((q) => `| \`${q.fn}(${q.args.map((a) => JSON.stringify(a)).join(", ")})\` | \`${JSON.stringify(q.answer)}\` |`);
const log = run.log.map((r) => `| \`${esc(r.call)}\` | ${r.status} | ${r.exec} | ${esc(r.refused ? `refused: ${r.refused}` : r.returned ?? "").slice(0, 140)} | ${tx(r.hash)} |`);
const first = Object.values(run.years)[0];

const md = `# BusinessDays: live run

Every year below was read by GenLayer validators on GenLayer Studio from two independent public calendars,
[Nager.Date](https://date.nager.at) and [OpenHolidays](https://www.openholidaysapi.org), on ${first.imported_at.slice(0, 10)}.
Contract \`${run.contract}\` ([explorer](${EXPLORER}/address/${run.contract})); \`node scripts/verify-code.mjs ${run.contract}\`
checks the deployed code is byte-identical to \`contracts/business_days.py\`.

## Country-years

"Only Nager.Date" / "Only OpenHolidays" are the nationwide public holidays one calendar lists and the other does not; a
year with any is DISPUTED and answers nothing. The digest is sha256 of both normalized calendars.

| Year | Status | Nager.Date | OpenHolidays | Only Nager.Date | Only OpenHolidays | Digest | Tx |
|---|---|---|---|---|---|---|---|
${rows.join("\n")}

Agreed tables:

${tables.join("\n")}

## Business-day answers

| View call | Answer |
|---|---|
${queries.join("\n")}

\`stats()\`: \`${JSON.stringify(run.stats)}\`

## Every transaction

A refused call is still ACCEPTED by consensus; the contract outcome is the \`exec\` column (\`ERROR\` = refused, on purpose).
Importer wallet \`${run.importer}\` (Studio test account).

| Call | Consensus | exec | Returned / refused | Tx |
|---|---|---|---|---|
${log.join("\n")}
`;
writeFileSync(new URL("../docs/REPRODUCTION.md", import.meta.url), md);
console.log(`wrote docs/REPRODUCTION.md (${run.log.length} transactions)`);
