# BusinessDays

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/license/mit/)

**Public holidays that two independent calendars agree on, read by GenLayer validators, and business-day arithmetic
over them: `is_business_day`, `add_business_days`, `business_days_between`.**

Payment terms, SLAs, notice periods, dispute windows and settlement dates are written in business days. A contract that
counts them needs each country's public holidays, and any single holiday source can be wrong or define "public holiday"
differently. BusinessDays only answers from years where two independent open calendars list exactly the same
nationwide public holidays, and records precisely where they disagree.

**Contract (GenLayer Studio):** [`0xbdcb82CDd1725F22Aa3afc447cf638aD265b908C`](https://explorer-studio.genlayer.com/address/0xbdcb82CDd1725F22Aa3afc447cf638aD265b908C)
(`node scripts/verify-code.mjs 0xbdcb82CDd1725F22Aa3afc447cf638aD265b908C` checks it is byte-identical to `contracts/business_days.py`).

## How a year is imported

`import_year(country, year)` (anyone; ISO 3166-1 alpha-2 country; years from five back to two ahead; one country-year
read again after a day at the earliest):

1. **Two calendars, independently.** Every validator reads
   - [Nager.Date](https://date.nager.at) `/api/v3/PublicHolidays/{year}/{country}`: entries with `global: true` and type
     `Public`;
   - [OpenHolidays](https://www.openholidaysapi.org) `/PublicHolidays`: entries with `nationwide: true`, type `Public`
     and `temporalScope` `FullDay` (half days are not days off), multi-day entries expanded day by day.
2. **Normalized, compared in code.** Each calendar becomes a sorted set of dates. Equal sets: **AGREED**. Different
   sets: **DISPUTED**, stored with `nager_only` and `openholidays_only`, the exact dates each calendar alone lists.
3. **Consensus.** Validators re-read both calendars and accept the leader's result only if they agree exactly on the
   status and on both normalized calendars, date by date (`same_reading`). The stored record carries a sha256 digest of
   both calendars, the import time and the importer.
4. **Refusals record nothing:** a country either calendar does not cover (no entries), an outage or a malformed
   response, a year out of range, a re-import within a day.

No model is involved: this is a web-grounded, deterministic primitive whose value is that validators independently
fetch both sources and must agree on every date. A re-import (a day later) replaces the record and keeps up to 8
earlier ones in `get_history`, so a calendar's correction is visible.

## Using it from another contract or app

| View | Returns |
|---|---|
| `is_business_day(country, day)` | `"yes"`; `"no"` for a Saturday, Sunday or AGREED public holiday; `"unknown"` for a weekday in a year that is not AGREED |
| `add_business_days(country, day, n)` | the date `n` business days after `day` (1 ≤ n ≤ 260), or `""` if it passes through a year that is not AGREED |
| `business_days_between(country, start, end)` | business days in `[start, end)` (at most three years), or `-1` if a year it needs is not AGREED |
| `holidays(country, year)` | the AGREED holidays as `[{date, name}]`, else `[]` |
| `status(country, year)` | `AGREED`, `DISPUTED` or `NOT_IMPORTED` |
| `get_year`, `get_history`, `list_years`, `stats` | the full record (both calendars, differences, names, digest), earlier records, paged summaries, counts |

Dates are `YYYY-MM-DD` and validated (no 2026-02-30); weekdays are computed from the date in code. Every loop is bounded
(`add_business_days` by `n`, `business_days_between` by three years, paged views by 100 rows).

## Verified live: nine country-years

`scripts/demo.mjs` ran on GenLayer Studio on 2026-11-23. Every date, difference, digest and transaction is in
[`docs/REPRODUCTION.md`](docs/REPRODUCTION.md).

| Year | Status | Where the calendars differ |
|---|---|---|
| Germany 2026, Germany 2027 | **AGREED** (9 holidays each) | — |
| France 2026 | **AGREED** (11) | — |
| Spain 2026 | **AGREED** (10) | — |
| Poland 2026 | **AGREED** (14) | — |
| Portugal 2026 | **AGREED** (13) | — |
| Netherlands 2026 | **DISPUTED** | only OpenHolidays lists 2026-04-03 (Good Friday) and 2026-05-05 (Liberation Day) as public holidays; Nager.Date types them as school/authority days, not general days off |
| Italy 2026 | **DISPUTED** | only Nager.Date lists 2026-04-05 (Easter Sunday) and 2026-10-04 (St. Francis of Assisi's Day) |
| Ireland 2027 | **DISPUTED** | the June bank holiday: Nager.Date 2027-06-07 (the first Monday of June), OpenHolidays 2027-06-04 (a Friday). One calendar is simply wrong, and no answer is taken from either |

Answers from the stored years:

| Call | Answer |
|---|---|
| `is_business_day("DE", "2026-12-24")` / `("DE", "2026-12-25")` | `yes` / `no` |
| `is_business_day("FR", "2026-07-14")` | `no` |
| `is_business_day("NL", "2026-04-03")`, `("IE", "2027-06-07")` | `unknown` (DISPUTED years) |
| `add_business_days("DE", "2026-12-23", 3)` | `2026-12-29` (24th; 25th, 26th and the weekend skipped; 28th, 29th) |
| `add_business_days("DE", "2026-12-30", 2)` | `2027-01-04` (across the new year, using both AGREED years) |
| `add_business_days("FR", "2026-05-07", 2)` | `2026-05-12` (8 May is Victory Day) |
| `add_business_days("NL", "2026-04-01", 5)` | `""` |
| `business_days_between("DE", "2026-01-01", "2027-01-01")` | `254` (261 weekdays, 7 holidays on weekdays) |
| `business_days_between("ES", "2026-12-01", "2027-01-01")` | `21` |
| `business_days_between("IT", "2026-06-01", "2026-07-01")` | `-1` |

Refused, recording nothing: the United States (OpenHolidays does not cover it), Germany 2026 again within a day, and 2035.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
genvm-lint check contracts/business_days.py
python -m pytest tests/direct -q                  # 41 direct-mode tests, both calendars mocked
npm install
node scripts/deploy.mjs                           # deploys to GenLayer Studio, prints the address
node scripts/demo.mjs <address>                   # the live run; writes docs/demo-run.json
node scripts/reproduction.mjs                     # renders docs/REPRODUCTION.md
node scripts/verify-code.mjs <address>
```

The tests cover agreed and disputed years (with the exact differences), the filters (regional, observance, half-day and
school entries excluded; multi-day entries expanded), countries or outages that cannot be read, malformed responses,
input validation, re-import after a day with history, and every view at weekends, holidays, across a new year and into a
year that is not imported.

## Limits

- Weekends are Saturday and Sunday: right for every country OpenHolidays covers today (36, mostly European).
- Nationwide public holidays only: regional holidays (a German state's, a Swiss canton's) are out of scope.
- Two calendars agreeing does not make them right; it makes a single source's mistake visible (Ireland 2027 above).
- A year is as of its import; `get_year(...).imported_at` lets a consumer re-import (after a day) or refuse old data.
- GenLayer Studio. The source carries the same Bradbury header switch as our other contracts.

Holiday data: [Nager.Date](https://github.com/nager/Nager.Date) (MIT) and [OpenHolidays API](https://www.openholidaysapi.org)
(Open Data).
