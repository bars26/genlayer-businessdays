// Live run of BusinessDays on GenLayer Studio: every validator reads Nager.Date and OpenHolidays for real
// country-years; then the business-day views are queried. Writes docs/demo-run.json.
//
//   node scripts/demo.mjs <contract-address>

import { writeFileSync } from "fs";
import { createAccount, generatePrivateKey } from "genlayer-js";
import { client, fund, log, read, setContract, sleep, write } from "./studio.mjs";

const [CONTRACT] = process.argv.slice(2);
if (!CONTRACT) {
  console.error("usage: node scripts/demo.mjs <contract-address>");
  process.exit(1);
}
setContract(CONTRACT);
const account = createAccount(generatePrivateKey());
const C = client(account);
await fund(account.address, 1n);
await sleep(3000);
console.log("contract", CONTRACT, "importer", account.address);

const years = [["DE", 2026], ["DE", 2027], ["FR", 2026], ["ES", 2026], ["PL", 2026], ["PT", 2026], ["NL", 2026], ["IT", 2026], ["IE", 2027]];
for (const [c, y] of years) {
  await write(C, "importer", "import_year", [c, y]);
  const r = JSON.parse(await read(C, "get_year", [c, y]));
  console.log(`  -> ${c}-${y}: ${r.status} | Nager.Date ${r.nager.length}, OpenHolidays ${r.openholidays.length}${r.status === "DISPUTED" ? ` | only Nager.Date ${JSON.stringify(r.nager_only)}, only OpenHolidays ${JSON.stringify(r.openholidays_only)}` : ""}`);
}
// Refused, recording nothing: a country OpenHolidays does not cover, the same year again within a day, a year out of range.
await write(C, "importer", "import_year", ["US", 2026], 0n, { expectError: true });
await write(C, "importer", "import_year", ["DE", 2026], 0n, { expectError: true });
await write(C, "importer", "import_year", ["DE", 2035], 0n, { expectError: true });

const queries = [
  ["is_business_day", ["DE", "2026-12-24"]], ["is_business_day", ["DE", "2026-12-25"]], ["is_business_day", ["FR", "2026-07-14"]],
  ["is_business_day", ["NL", "2026-04-03"]], ["is_business_day", ["IE", "2027-06-07"]],
  ["add_business_days", ["DE", "2026-12-23", 3]], ["add_business_days", ["DE", "2026-12-30", 2]], ["add_business_days", ["FR", "2026-05-07", 2]],
  ["add_business_days", ["NL", "2026-04-01", 5]],
  ["business_days_between", ["DE", "2026-01-01", "2027-01-01"]], ["business_days_between", ["ES", "2026-12-01", "2027-01-01"]],
  ["business_days_between", ["IT", "2026-06-01", "2026-07-01"]],
];
const answers = [];
for (const [fn, args] of queries) {
  const a = await read(C, fn, args);
  answers.push({ fn, args, answer: typeof a === "bigint" ? Number(a) : a });
  console.log(`  ${fn}(${args.join(", ")}) = ${a}`);
}
const out = { network: "studio", contract: CONTRACT, importer: account.address, log, queries: answers, years: {},
  list: JSON.parse(await read(C, "list_years", [0, 50])), stats: JSON.parse(await read(C, "stats")) };
for (const [c, y] of years) out.years[`${c}-${y}`] = JSON.parse(await read(C, "get_year", [c, y]));
writeFileSync(new URL("../docs/demo-run.json", import.meta.url), JSON.stringify(out, null, 2));
console.log("stats", JSON.stringify(out.stats));
console.log("wrote docs/demo-run.json");
