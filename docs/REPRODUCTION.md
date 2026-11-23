# BusinessDays: live run

Every year below was read by GenLayer validators on GenLayer Studio from two independent public calendars,
[Nager.Date](https://date.nager.at) and [OpenHolidays](https://www.openholidaysapi.org), on 2026-11-23.
Contract `0xbdcb82CDd1725F22Aa3afc447cf638aD265b908C` ([explorer](https://explorer-studio.genlayer.com/address/0xbdcb82CDd1725F22Aa3afc447cf638aD265b908C)); `node scripts/verify-code.mjs 0xbdcb82CDd1725F22Aa3afc447cf638aD265b908C`
checks the deployed code is byte-identical to `contracts/business_days.py`.

## Country-years

"Only Nager.Date" / "Only OpenHolidays" are the nationwide public holidays one calendar lists and the other does not; a
year with any is DISPUTED and answers nothing. The digest is sha256 of both normalized calendars.

| Year | Status | Nager.Date | OpenHolidays | Only Nager.Date | Only OpenHolidays | Digest | Tx |
|---|---|---|---|---|---|---|---|
| DE-2026 | **AGREED** | 9 | 9 | — | — | `204e31854e6aec1c…` | [0x94a4f7ba…](https://explorer-studio.genlayer.com/tx/0x94a4f7bac3837627342ad8c8fcb1167966c0c41ce72a951d1393acb85d557187) |
| DE-2027 | **AGREED** | 9 | 9 | — | — | `754ad0bb1d8d830e…` | [0x863c21ed…](https://explorer-studio.genlayer.com/tx/0x863c21ed69b77f93fd4932e24b42ef9b3ca4e19e185841f230795d07b335b65d) |
| FR-2026 | **AGREED** | 11 | 11 | — | — | `eb419efa249abc4d…` | [0xc65efc73…](https://explorer-studio.genlayer.com/tx/0xc65efc731ed6143a945888e4a8f1a8ac708acb2795acf625d4ce986f2cec5aae) |
| ES-2026 | **AGREED** | 10 | 10 | — | — | `ed4de428998a5728…` | [0x26086361…](https://explorer-studio.genlayer.com/tx/0x26086361a27660891eae07b9d628f2f715bc7236d539debfba182f54b9ed2c57) |
| PL-2026 | **AGREED** | 14 | 14 | — | — | `875f3a8337e3f2cf…` | [0xb57bc6b2…](https://explorer-studio.genlayer.com/tx/0xb57bc6b20b1549c2eb30e187c181accb329537313e3d91cb79d4bc838b1a8271) |
| PT-2026 | **AGREED** | 13 | 13 | — | — | `97bd1fb490c9e7df…` | [0x645a0e0c…](https://explorer-studio.genlayer.com/tx/0x645a0e0c4f6f5cd979bc1d9e3fd54a4913cdf8127758ceb887dce05ec023b3e7) |
| NL-2026 | **DISPUTED** | 9 | 11 | — | 2026-04-03 Good Friday; 2026-05-05 Liberation Day | `d0159e7ec76ed3a9…` | [0x6533dd74…](https://explorer-studio.genlayer.com/tx/0x6533dd741e63ba7f52186fde70f70c4b9f39bb1387217d3f97172af319201dec) |
| IT-2026 | **DISPUTED** | 13 | 11 | 2026-04-05 Easter Sunday; 2026-10-04 St. Francis of Assisi's Day | — | `a13aff041254ab54…` | [0xb3f3ce24…](https://explorer-studio.genlayer.com/tx/0xb3f3ce2441be609446274bf0b128b45e1b7a83a1dba7b08b65dd523fb658324c) |
| IE-2027 | **DISPUTED** | 10 | 10 | 2027-06-07 June Holiday | 2027-06-04 June Holiday | `641618ad412654dd…` | [0xdfa8f731…](https://explorer-studio.genlayer.com/tx/0xdfa8f73147d433b04878d2f7296f4a47192935cd2f13da9385be86b200ff3b2e) |

Agreed tables:

- **DE-2026**: 2026-01-01 New Year's Day, 2026-04-03 Good Friday, 2026-04-06 Easter Monday, 2026-05-01 Labour Day, 2026-05-14 Ascension Day, 2026-05-25 Whit Monday, 2026-10-03 German Unity Day, 2026-12-25 Christmas Day, 2026-12-26 St. Stephen's Day
- **DE-2027**: 2027-01-01 New Year's Day, 2027-03-26 Good Friday, 2027-03-29 Easter Monday, 2027-05-01 Labour Day, 2027-05-06 Ascension Day, 2027-05-17 Whit Monday, 2027-10-03 German Unity Day, 2027-12-25 Christmas Day, 2027-12-26 St. Stephen's Day
- **FR-2026**: 2026-01-01 New Year's Day, 2026-04-06 Easter Monday, 2026-05-01 Labour Day, 2026-05-08 Victory in Europe Day, 2026-05-14 Ascension Day, 2026-05-25 Whit Monday, 2026-07-14 Bastille Day, 2026-08-15 Assumption Day, 2026-11-01 All Saints' Day, 2026-11-11 Armistice Day, 2026-12-25 Christmas Day
- **ES-2026**: 2026-01-01 New Year's Day, 2026-01-06 Epiphany, 2026-04-03 Good Friday, 2026-05-01 Labour Day, 2026-08-15 Assumption, 2026-10-12 National Day of Spain, 2026-11-01 All Saints Day, 2026-12-06 Constitution Day, 2026-12-08 Immaculate Conception, 2026-12-25 Christmas Day
- **PL-2026**: 2026-01-01 New Year's Day, 2026-01-06 Epiphany, 2026-04-05 Easter Sunday, 2026-04-06 Easter Monday, 2026-05-01 May Day, 2026-05-03 Constitution Day, 2026-05-24 Pentecost, 2026-06-04 Corpus Christi, 2026-08-15 Assumption Day, 2026-11-01 All Saints' Day, 2026-11-11 Independence Day, 2026-12-24 Christmas Eve, 2026-12-25 Christmas Day, 2026-12-26 St. Stephen's Day
- **PT-2026**: 2026-01-01 New Year's Day, 2026-04-03 Good Friday, 2026-04-05 Easter Sunday, 2026-04-25 Freedom Day, 2026-05-01 Labour Day, 2026-06-04 Corpus Christi, 2026-06-10 National Day, 2026-08-15 Assumption Day, 2026-10-05 Republic Day, 2026-11-01 All Saints Day, 2026-12-01 Restoration of Independence, 2026-12-08 Immaculate Conception, 2026-12-25 Christmas Day

## Business-day answers

| View call | Answer |
|---|---|
| `is_business_day("DE", "2026-12-24")` | `"yes"` |
| `is_business_day("DE", "2026-12-25")` | `"no"` |
| `is_business_day("FR", "2026-07-14")` | `"no"` |
| `is_business_day("NL", "2026-04-03")` | `"unknown"` |
| `is_business_day("IE", "2027-06-07")` | `"unknown"` |
| `add_business_days("DE", "2026-12-23", 3)` | `"2026-12-29"` |
| `add_business_days("DE", "2026-12-30", 2)` | `"2027-01-04"` |
| `add_business_days("FR", "2026-05-07", 2)` | `"2026-05-12"` |
| `add_business_days("NL", "2026-04-01", 5)` | `""` |
| `business_days_between("DE", "2026-01-01", "2027-01-01")` | `254` |
| `business_days_between("ES", "2026-12-01", "2027-01-01")` | `21` |
| `business_days_between("IT", "2026-06-01", "2026-07-01")` | `-1` |

`stats()`: `{"years":9,"imports":9}`

## Every transaction

A refused call is still ACCEPTED by consensus; the contract outcome is the `exec` column (`ERROR` = refused, on purpose).
Importer wallet `0x99f92701Bf6B7E0899F019A895c570E939d7752D` (Studio test account).

| Call | Consensus | exec | Returned / refused | Tx |
|---|---|---|---|---|
| `import_year("DE", 2026)` | ACCEPTED | SUCCESS | AGREED | [0x94a4f7ba…](https://explorer-studio.genlayer.com/tx/0x94a4f7bac3837627342ad8c8fcb1167966c0c41ce72a951d1393acb85d557187) |
| `import_year("DE", 2027)` | ACCEPTED | SUCCESS | AGREED | [0x863c21ed…](https://explorer-studio.genlayer.com/tx/0x863c21ed69b77f93fd4932e24b42ef9b3ca4e19e185841f230795d07b335b65d) |
| `import_year("FR", 2026)` | ACCEPTED | SUCCESS | AGREED | [0xc65efc73…](https://explorer-studio.genlayer.com/tx/0xc65efc731ed6143a945888e4a8f1a8ac708acb2795acf625d4ce986f2cec5aae) |
| `import_year("ES", 2026)` | ACCEPTED | SUCCESS | AGREED | [0x26086361…](https://explorer-studio.genlayer.com/tx/0x26086361a27660891eae07b9d628f2f715bc7236d539debfba182f54b9ed2c57) |
| `import_year("PL", 2026)` | ACCEPTED | SUCCESS | AGREED | [0xb57bc6b2…](https://explorer-studio.genlayer.com/tx/0xb57bc6b20b1549c2eb30e187c181accb329537313e3d91cb79d4bc838b1a8271) |
| `import_year("PT", 2026)` | ACCEPTED | SUCCESS | AGREED | [0x645a0e0c…](https://explorer-studio.genlayer.com/tx/0x645a0e0c4f6f5cd979bc1d9e3fd54a4913cdf8127758ceb887dce05ec023b3e7) |
| `import_year("NL", 2026)` | ACCEPTED | SUCCESS | DISPUTED | [0x6533dd74…](https://explorer-studio.genlayer.com/tx/0x6533dd741e63ba7f52186fde70f70c4b9f39bb1387217d3f97172af319201dec) |
| `import_year("IT", 2026)` | ACCEPTED | SUCCESS | DISPUTED | [0xb3f3ce24…](https://explorer-studio.genlayer.com/tx/0xb3f3ce2441be609446274bf0b128b45e1b7a83a1dba7b08b65dd523fb658324c) |
| `import_year("IE", 2027)` | ACCEPTED | SUCCESS | DISPUTED | [0xdfa8f731…](https://explorer-studio.genlayer.com/tx/0xdfa8f73147d433b04878d2f7296f4a47192935cd2f13da9385be86b200ff3b2e) |
| `import_year("US", 2026)` | ACCEPTED | ERROR | refused: OpenHolidays lists no public holidays for US-2026: the country is not covered by both calendars | [0x6deb0ce0…](https://explorer-studio.genlayer.com/tx/0x6deb0ce0cea88cead9e602f1050d48772d7091fc2507b6a13cc776c2ab39aadd) |
| `import_year("DE", 2026)` | ACCEPTED | ERROR | refused: DE-2026 was imported at 2026-11-23 13:13:02 UTC; a year is read again after a day | [0x98e986c1…](https://explorer-studio.genlayer.com/tx/0x98e986c14b1c4fd4addbb3302e2df140b6456a5a8b84ee863376f8d651fce649) |
| `import_year("DE", 2035)` | ACCEPTED | ERROR | refused: year must be from 2021 to 2028 | [0xda44032f…](https://explorer-studio.genlayer.com/tx/0xda44032ffb3300592f62bba688f05ba72038adb15a008588c9de6a8516d65a89) |
