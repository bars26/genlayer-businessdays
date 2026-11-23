# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""BusinessDays: public holidays that two independent calendars agree on, and business-day arithmetic over them.

Deadlines, payment terms, SLAs and notice periods are written in business days, and a contract that counts them needs
each country's public holidays. Any one holiday source can be wrong or define "public holiday" differently. Here every
validator reads two independent open calendars for a country and year:

    Nager.Date      https://date.nager.at  (nationwide entries of type "Public")
    OpenHolidays    https://openholidaysapi.org  (nationwide, full-day entries of type "Public")

and normalizes each to a set of dates. Equal sets: the year is AGREED and stored. Different sets: the year is DISPUTED
and stored with exactly which dates each calendar alone lists; nothing is answered from it. Validators must agree
exactly on both normalized calendars, so a stored table is what every validator read.

Views answer from AGREED years only: `is_business_day` ("yes" / "no" / "unknown"), `add_business_days`,
`business_days_between` (both "" / -1 when a year they need is not AGREED). Weekends are Saturday and Sunday.
"""

import hashlib
import json
import re

import genlayer

# One source for both networks (GenLayer Studio's runner above; Bradbury's py-genlayer:babwp… uses `import genlayer as gl`).
if hasattr(genlayer, "gl"):  # GenLayer Studio
    from genlayer import *

    _Contract = gl.Contract

    def _message_raw() -> dict:
        return gl.message_raw
else:  # Bradbury Phase 2
    import genlayer as gl
    from genlayer.types import *
    from genlayer.storage import TreeMap, DynArray

    _Contract = gl.contract.Contract

    def _message_raw() -> dict:
        return gl.message.raw


_Err = gl.vm.UserError

AGREED, DISPUTED = "AGREED", "DISPUTED"
_NAGER = "https://date.nager.at/api/v3/PublicHolidays"
_OPEN = "https://openholidaysapi.org/PublicHolidays"
_HEADERS = {"accept": "application/json", "user-agent": "BusinessDays/1.0 (GenLayer; github.com/bars26/genlayer-businessdays)"}
_DAY = 86400
_YEARS_BACK, _YEARS_AHEAD = 5, 2  # a year from five years ago to two years ahead can be imported
_REIMPORT_SECONDS = _DAY  # an imported year can be read again after a day (calendars get corrected)
_MAX_SPAN_DAYS = 3 * 366  # business_days_between covers at most three years
_MAX_ADD = 260  # add_business_days moves at most a year of business days
_HISTORY_LIMIT = 8


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _days(day: str) -> int:
    """Days since 1970-01-01 for "YYYY-MM-DD" (proleptic Gregorian), without datetime."""
    y, m, d = int(day[0:4]), int(day[5:7]), int(day[8:10])
    a = (14 - m) // 12
    yy, mm = y + 4800 - a, m + 12 * a - 3
    return d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - yy // 100 + yy // 400 - 32045 - 2440588


def _date(days: int) -> str:
    """"YYYY-MM-DD" for days since 1970-01-01."""
    j = days + 2440588 + 32044
    g, dg = j // 146097, j % 146097
    c = (dg // 36524 + 1) * 3 // 4
    dc = dg - c * 36524
    b, db = dc // 1461, dc % 1461
    a = (db // 365 + 1) * 3 // 4
    da = db - a * 365
    y = g * 400 + c * 100 + b * 4 + a
    m = (da * 5 + 308) // 153 - 2
    d = da - (m + 4) * 153 // 5 + 122
    return f"{y - 4800 + (m + 2) // 12:04d}-{(m + 2) % 12 + 1:02d}-{d + 1:02d}"


def _seconds(iso: str) -> int:
    """Seconds since 1970 for "YYYY-MM-DDTHH:MM:SS" (UTC)."""
    return _days(iso[:10]) * _DAY + int(iso[11:13] or 0) * 3600 + int(iso[14:16] or 0) * 60 + int(iso[17:19] or 0)


def _valid_day(day: str) -> bool:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", day or ""):
        return False
    return _date(_days(day)) == day  # rejects 2026-02-30 and the like


def _weekday(day: str) -> int:
    """0 = Monday … 6 = Sunday (1970-01-01 was a Thursday)."""
    return (_days(day) + 3) % 7


# --- the two calendars -------------------------------------------------------------------------------------------------


def _get_json(url: str) -> tuple:
    """("ok", JSON) / ("none", None) for 204, 404 or an empty list / ("error", None)."""
    try:
        response = gl.nondet.web.get(url, headers=_HEADERS)
    except Exception:
        return "error", None
    if response.status in (204, 404):
        return "none", None
    if response.status != 200:
        return "error", None
    try:
        data = json.loads((response.body or b"").decode("utf-8", errors="replace") or "null")
    except ValueError:
        return "error", None
    if not isinstance(data, list):
        return "error", None
    return ("ok", data) if data else ("none", None)


def _nager(country: str, year: int) -> tuple:
    state, data = _get_json(f"{_NAGER}/{year}/{country}")
    if state != "ok":
        return state, None
    out = {}
    for h in data:
        if not isinstance(h, dict) or not h.get("global") or "Public" not in (h.get("types") or []):
            continue
        day = str(h.get("date") or "")
        if _valid_day(day) and day[:4] == str(year):
            out[day] = str(h.get("name") or h.get("localName") or "")[:80]
    return "ok", out


def _open_holidays(country: str, year: int) -> tuple:
    state, data = _get_json(f"{_OPEN}?countryIsoCode={country}&languageIsoCode=EN&validFrom={year}-01-01&validTo={year}-12-31")
    if state != "ok":
        return state, None
    out = {}
    for h in data:
        if not isinstance(h, dict) or h.get("type") != "Public" or h.get("nationwide") is not True:
            continue
        if (h.get("temporalScope") or "FullDay") != "FullDay":
            continue  # a half day off is not a day off
        start, end = str(h.get("startDate") or ""), str(h.get("endDate") or "")
        if not (_valid_day(start) and _valid_day(end)) or _days(end) < _days(start) or _days(end) - _days(start) > 31:
            continue
        names = h.get("name") or []
        name = next((str(n.get("text") or "") for n in names if isinstance(n, dict) and n.get("language") == "EN"), "")
        for d in range(_days(start), _days(end) + 1):
            day = _date(d)
            if day[:4] == str(year):
                out[day] = name[:80]
    return "ok", out


def read_year(country: str, year: int) -> dict:
    """One validator's reading of both calendars for a country and year."""
    ns, nager = _nager(country, year)
    os_, oh = _open_holidays(country, year)
    if "error" in (ns, os_):
        return {"state": "error", "what": "Nager.Date" if ns == "error" else "OpenHolidays"}
    if ns == "none" or os_ == "none":
        return {"state": "none", "what": "Nager.Date" if ns == "none" else "OpenHolidays"}
    n, o = sorted(nager), sorted(oh)
    out = {"state": "ok", "country": country, "year": year, "nager": n, "openholidays": o,
           "nager_only": sorted(set(n) - set(o)), "openholidays_only": sorted(set(o) - set(n))}
    out["status"] = AGREED if n == o else DISPUTED
    # names for display: Nager.Date's English names, OpenHolidays' where Nager.Date has none
    out["names"] = {d: nager.get(d) or oh.get(d, "") for d in sorted(set(n) | set(o))}
    out["digest"] = _sha256(json.dumps({"nager": n, "openholidays": o}, sort_keys=True))
    return out


def same_reading(a: dict, b: dict) -> bool:
    """Validators agree on the status and on both normalized calendars, date by date."""
    keys = ("state", "what", "status", "country", "year", "nager", "openholidays")
    return all(a.get(k) == b.get(k) for k in keys)


def _validator(read):
    def validator_fn(leader_result) -> bool:
        if not isinstance(leader_result, gl.vm.Return):
            return False
        try:
            return same_reading(json.loads(leader_result.calldata), json.loads(read()))
        except Exception:
            return False

    return validator_fn


class BusinessDays(_Contract):
    years: TreeMap[str, str]  # "DE-2026" -> the latest agreed reading (JSON)
    history: TreeMap[str, str]  # "DE-2026" -> earlier readings' summaries (JSON list)
    keys: DynArray[str]  # every country-year ever imported, in first-import order
    n_imports: u256

    def __init__(self):
        self.n_imports = u256(0)

    def _now(self) -> str:
        return _message_raw()["datetime"][:19]

    def _country(self, country: str) -> str:
        c = str(country or "").strip().upper()
        if not re.match(r"^[A-Z]{2}$", c):
            raise _Err("country must be a two-letter ISO 3166-1 code, like DE")
        return c

    def _date_arg(self, name: str, day: str) -> str:
        d = str(day or "").strip()
        if not _valid_day(d):
            raise _Err(f"{name} must be a date YYYY-MM-DD")
        return d

    def _year(self, country: str, year: int) -> dict:
        raw = self.years.get(f"{country}-{year}", "")
        return json.loads(raw) if raw else {}

    def _closed(self, country: str, day: str):
        """True if `day` is a weekend or an AGREED public holiday, False if a business day, None if unknown."""
        if _weekday(day) >= 5:
            return True
        y = self._year(country, int(day[:4]))
        if y.get("status") != AGREED:
            return None
        return day in y["nager"]

    @gl.public.write
    def import_year(self, country: str, year: int) -> str:
        """Read a country's public holidays for a year from both calendars. Returns "AGREED" or "DISPUTED"."""
        c = self._country(country)
        now = self._now()
        this_year = int(now[:4])
        y = int(year)
        if not this_year - _YEARS_BACK <= y <= this_year + _YEARS_AHEAD:
            raise _Err(f"year must be from {this_year - _YEARS_BACK} to {this_year + _YEARS_AHEAD}")
        key = f"{c}-{y}"
        prev = self._year(c, y)
        if prev and _seconds(now) - _seconds(prev["imported_at"]) < _REIMPORT_SECONDS:
            raise _Err(f"{key} was imported at {prev['imported_at'].replace('T', ' ')} UTC; a year is read again after a day")

        def run() -> str:
            return json.dumps(read_year(c, y), sort_keys=True)

        r = json.loads(gl.vm.run_nondet(run, _validator(run)))
        if r["state"] == "none":
            raise _Err(f"{r['what']} lists no public holidays for {key}: the country is not covered by both calendars")
        if r["state"] != "ok":
            raise _Err(f"{r['what']} could not be read right now; nothing was recorded")
        del r["state"]
        r["imported_at"] = now
        r["imported_by"] = gl.message.sender_address.as_hex.lower()
        if prev:
            past = json.loads(self.history.get(key, "") or "[]")
            past.append({k: prev.get(k) for k in ("imported_at", "status", "digest", "nager_only", "openholidays_only")})
            self.history[key] = json.dumps(past[-_HISTORY_LIMIT:], sort_keys=True)
        else:
            self.keys.append(key)
        self.years[key] = json.dumps(r, sort_keys=True)
        self.n_imports = u256(int(self.n_imports) + 1)
        return r["status"]

    # --- views ---------------------------------------------------------------------------------------------------------

    @gl.public.view
    def get_year(self, country: str, year: int) -> str:
        """The latest reading of a country-year as JSON (both calendars, the difference, names, digest), or ""."""
        return self.years.get(f"{self._country(country)}-{int(year)}", "")

    @gl.public.view
    def get_history(self, country: str, year: int) -> str:
        return self.history.get(f"{self._country(country)}-{int(year)}", "") or "[]"

    @gl.public.view
    def status(self, country: str, year: int) -> str:
        """"AGREED", "DISPUTED" or "NOT_IMPORTED"."""
        return self._year(self._country(country), int(year)).get("status", "NOT_IMPORTED")

    @gl.public.view
    def holidays(self, country: str, year: int) -> str:
        """The AGREED public holidays of a country-year as a JSON list of {date, name}; "[]" otherwise."""
        y = self._year(self._country(country), int(year))
        if y.get("status") != AGREED:
            return "[]"
        return json.dumps([{"date": d, "name": y["names"].get(d, "")} for d in y["nager"]])

    @gl.public.view
    def is_business_day(self, country: str, day: str) -> str:
        """"yes", "no" (a weekend or an AGREED public holiday) or "unknown" (a weekday in a year not AGREED)."""
        off = self._closed(self._country(country), self._date_arg("day", day))
        return "unknown" if off is None else ("no" if off else "yes")

    @gl.public.view
    def add_business_days(self, country: str, day: str, n: int) -> str:
        """The date `n` business days after `day` (n from 1 to 260), or "" if a year it passes through is not AGREED."""
        c, d = self._country(country), self._date_arg("day", day)
        count = int(n)
        if not 1 <= count <= _MAX_ADD:
            raise _Err(f"n must be from 1 to {_MAX_ADD}")
        t = _days(d)
        while count > 0:  # bounded: at most n business days plus the weekends and holidays between them
            t += 1
            off = self._closed(c, _date(t))
            if off is None:
                return ""
            if not off:
                count -= 1
        return _date(t)

    @gl.public.view
    def business_days_between(self, country: str, start: str, end: str) -> int:
        """Business days in [start, end) (at most three years), or -1 if a year it needs is not AGREED."""
        c, a, b = self._country(country), self._date_arg("start", start), self._date_arg("end", end)
        if _days(b) < _days(a) or _days(b) - _days(a) > _MAX_SPAN_DAYS:
            raise _Err("end must be on or after start, at most three years later")
        total = 0
        for t in range(_days(a), _days(b)):
            off = self._closed(c, _date(t))
            if off is None:
                return -1
            if not off:
                total += 1
        return total

    @gl.public.view
    def list_years(self, offset: int, limit: int) -> str:
        """Summaries of imported country-years in first-import order, as JSON."""
        start, count = max(int(offset), 0), max(min(int(limit), 100), 0)
        rows = []
        for i in range(start, min(len(self.keys), start + count)):
            y = json.loads(self.years[self.keys[i]])
            rows.append({"key": self.keys[i], "status": y["status"], "holidays": len(y["nager"]) if y["status"] == AGREED else None,
                         "nager_only": y["nager_only"], "openholidays_only": y["openholidays_only"], "imported_at": y["imported_at"]})
        return json.dumps(rows, sort_keys=True)

    @gl.public.view
    def stats(self) -> str:
        return json.dumps({"years": len(self.keys), "imports": int(self.n_imports)})


del _Contract  # the schema tools take the first Contract class they find in the module: leave only BusinessDays
