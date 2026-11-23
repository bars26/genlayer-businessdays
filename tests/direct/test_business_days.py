"""Direct-mode tests for BusinessDays: public holidays agreed by two independent calendars, and business-day arithmetic."""

import json
import re
import sys

import pytest

from tests.direct.conftest import CONTRACT_PATH

NAGER = "https://date.nager.at/api/v3/PublicHolidays"
OPEN = "https://openholidaysapi.org/PublicHolidays"
DE_2026 = {"2026-01-01": "New Year's Day", "2026-04-03": "Good Friday", "2026-04-06": "Easter Monday", "2026-05-01": "Labour Day",
           "2026-05-14": "Ascension Day", "2026-05-25": "Whit Monday", "2026-10-03": "German Unity Day",
           "2026-12-25": "Christmas Day", "2026-12-26": "St. Stephen's Day"}
DE_2027 = {"2027-01-01": "New Year's Day", "2027-03-26": "Good Friday", "2027-03-29": "Easter Monday", "2027-05-01": "Labour Day",
           "2027-05-06": "Ascension Day", "2027-05-17": "Whit Monday", "2027-10-03": "German Unity Day",
           "2027-12-25": "Christmas Day", "2027-12-26": "St. Stephen's Day"}


def _nager_rows(days, extra=()):
    rows = [{"date": d, "name": n, "localName": n, "global": True, "types": ["Public"]} for d, n in days.items()]
    rows += list(extra)
    return rows


def _open_rows(days, extra=()):
    rows = [{"startDate": d, "endDate": d, "type": "Public", "nationwide": True, "temporalScope": "FullDay",
             "name": [{"language": "EN", "text": n}]} for d, n in days.items()]
    rows += list(extra)
    return rows


def _web(vm, url, body, status=200):
    vm.mock_web("^" + re.escape(url) + "$", {"method": "GET", "response": {
        "status": status, "headers": {"Content-Type": b"application/json"}, "body": json.dumps(body).encode()}})


def _calendars(vm, country, year, nager, open_, nager_status=200, open_status=200):
    _web(vm, f"{NAGER}/{year}/{country}", nager, nager_status)
    _web(vm, f"{OPEN}?countryIsoCode={country}&languageIsoCode=EN&validFrom={year}-01-01&validTo={year}-12-31", open_, open_status)


def _at(vm, ts):
    """Move the clock (warp() does not reach a deployed contract's message datetime, so set it too)."""
    vm.warp(ts)
    raw = getattr(sys.modules.get("genlayer.gl"), "message_raw", None)
    if isinstance(raw, dict):
        raw["datetime"] = ts


@pytest.fixture
def bd(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    _at(direct_vm, "2026-11-23T12:00:00Z")
    return direct_deploy(CONTRACT_PATH)


def _import(vm, bd, country="DE", year=2026, days=DE_2026, nager=None, open_=None, **status):
    vm.clear_mocks()
    _calendars(vm, country, year, _nager_rows(days) if nager is None else nager, _open_rows(days) if open_ is None else open_, **status)
    return bd.import_year(country, year)


# --- importing a year ------------------------------------------------------------------------------------------------------


def test_two_equal_calendars_make_an_agreed_year(direct_vm, bd):
    assert _import(direct_vm, bd) == "AGREED"
    y = json.loads(bd.get_year("de", 2026))
    assert (y["status"], y["country"], y["year"], y["nager"], y["nager_only"], y["openholidays_only"]) == \
        ("AGREED", "DE", 2026, sorted(DE_2026), [], [])
    assert len(y["digest"]) == 64 and y["imported_at"] == "2026-11-23T12:00:00"
    assert json.loads(bd.holidays("DE", 2026))[0] == {"date": "2026-01-01", "name": "New Year's Day"}
    assert bd.status("DE", 2026) == "AGREED" and bd.status("DE", 2027) == "NOT_IMPORTED"


def test_calendars_that_differ_make_a_disputed_year_with_the_difference(direct_vm, bd):
    nl = {"2026-01-01": "New Year's Day", "2026-04-05": "Easter Sunday", "2026-04-06": "Easter Monday", "2026-12-25": "Christmas Day"}
    open_only = dict(nl, **{"2026-04-03": "Good Friday", "2026-05-05": "Liberation Day"})
    assert _import(direct_vm, bd, "NL", 2026, nager=_nager_rows(nl), open_=_open_rows(open_only)) == "DISPUTED"
    y = json.loads(bd.get_year("NL", 2026))
    assert (y["nager_only"], y["openholidays_only"]) == ([], ["2026-04-03", "2026-05-05"])
    assert y["names"]["2026-05-05"] == "Liberation Day"  # names for display come from either calendar
    assert bd.holidays("NL", 2026) == "[]"
    assert bd.is_business_day("NL", "2026-04-03") == "unknown"  # a weekday in a disputed year
    assert bd.is_business_day("NL", "2026-04-04") == "no"  # a Saturday is known without the calendars


def test_only_nationwide_full_day_public_holidays_count(direct_vm, bd):
    nager = _nager_rows(DE_2026, extra=[
        {"date": "2026-01-06", "name": "Epiphany", "global": False, "counties": ["DE-BW"], "types": ["Public"]},
        {"date": "2026-12-24", "name": "Christmas Eve", "global": True, "types": ["Observance"]}])
    open_ = _open_rows(DE_2026, extra=[
        {"startDate": "2026-01-06", "endDate": "2026-01-06", "type": "Public", "nationwide": False, "name": []},
        {"startDate": "2026-12-24", "endDate": "2026-12-24", "type": "Public", "nationwide": True, "temporalScope": "HalfDay", "name": []},
        {"startDate": "2026-07-20", "endDate": "2026-08-31", "type": "School", "nationwide": True, "name": []}])
    assert _import(direct_vm, bd, nager=nager, open_=open_) == "AGREED"
    assert json.loads(bd.get_year("DE", 2026))["nager"] == sorted(DE_2026)


def test_a_multi_day_holiday_counts_each_day(direct_vm, bd):
    days = {"2026-01-01": "New Year", "2026-01-02": "New Year (2)"}
    open_ = _open_rows({}, extra=[{"startDate": "2026-01-01", "endDate": "2026-01-02", "type": "Public", "nationwide": True,
                                   "name": [{"language": "EN", "text": "New Year"}]}])
    assert _import(direct_vm, bd, "SI", 2026, nager=_nager_rows(days), open_=open_) == "AGREED"


@pytest.mark.parametrize("status, reason", [
    (dict(nager_status=404), "Nager.Date lists no public holidays"),
    (dict(open_=[]), "OpenHolidays lists no public holidays"),
    (dict(nager_status=503), "Nager.Date could not be read right now"),
    (dict(open_status=500), "OpenHolidays could not be read right now"),
])
def test_a_country_or_outage_that_cannot_be_read_records_nothing(direct_vm, bd, status, reason):
    open_ = status.pop("open_", None)
    with direct_vm.expect_revert(reason):
        _import(direct_vm, bd, "US", 2026, open_=open_, **status)
    assert bd.status("US", 2026) == "NOT_IMPORTED" and json.loads(bd.stats())["imports"] == 0


@pytest.mark.parametrize("country, year, reason", [
    ("DEU", 2026, "two-letter ISO"), ("1A", 2026, "two-letter ISO"), ("DE", 2020, "year must be from 2021 to 2028"),
    ("DE", 2029, "year must be from 2021 to 2028"),
])
def test_bad_requests_are_refused_before_any_reading(direct_vm, bd, country, year, reason):
    direct_vm.clear_mocks()
    with direct_vm.expect_revert(reason):
        bd.import_year(country, year)


def test_a_year_is_read_again_after_a_day_and_keeps_history(direct_vm, bd):
    nager = dict(DE_2026)
    del nager["2026-10-03"]
    assert _import(direct_vm, bd, nager=_nager_rows(nager)) == "DISPUTED"
    with direct_vm.expect_revert("a year is read again after a day"):
        _import(direct_vm, bd)
    _at(direct_vm, "2026-11-24T12:00:00Z")
    assert _import(direct_vm, bd) == "AGREED"  # the calendar was corrected
    past = json.loads(bd.get_history("DE", 2026))
    assert len(past) == 1 and past[0]["status"] == "DISPUTED" and past[0]["openholidays_only"] == ["2026-10-03"]
    assert json.loads(bd.stats()) == {"years": 1, "imports": 2}
    assert json.loads(bd.list_years(0, 10)) == [{"key": "DE-2026", "status": "AGREED", "holidays": 9, "nager_only": [],
                                                 "openholidays_only": [], "imported_at": "2026-11-24T12:00:00"}]


def test_a_response_that_is_not_a_list_records_nothing(direct_vm, bd):
    direct_vm.clear_mocks()
    _calendars(direct_vm, "DE", 2026, {"error": "nope"}, _open_rows(DE_2026))
    with direct_vm.expect_revert("could not be read right now"):
        bd.import_year("DE", 2026)


# --- business-day arithmetic -----------------------------------------------------------------------------------------------


@pytest.fixture
def de(direct_vm, bd):
    _import(direct_vm, bd)
    _import(direct_vm, bd, year=2027, days=DE_2027)
    return bd


@pytest.mark.parametrize("day, answer", [
    ("2026-12-24", "yes"), ("2026-12-25", "no"), ("2026-12-26", "no"), ("2026-12-28", "yes"), ("2026-11-28", "no"),
    ("2026-10-03", "no"), ("2027-01-01", "no"), ("2027-01-04", "yes"), ("2028-01-03", "unknown"), ("2028-01-01", "no"),
])
def test_is_business_day(de, day, answer):
    assert de.is_business_day("DE", day) == answer


@pytest.mark.parametrize("day, n, answer", [
    ("2026-12-23", 1, "2026-12-24"), ("2026-12-23", 2, "2026-12-28"), ("2026-12-23", 3, "2026-12-29"),
    ("2026-12-30", 2, "2027-01-04"),  # across the new year: Dec 31, (Jan 1 holiday, weekend), Jan 4
    ("2026-04-02", 1, "2026-04-07"),  # Good Friday, the weekend and Easter Monday are skipped
    ("2027-12-20", 10, ""),  # runs into 2028, which is not imported
])
def test_add_business_days(de, day, n, answer):
    assert de.add_business_days("DE", day, n) == answer


@pytest.mark.parametrize("start, end, answer", [
    ("2026-12-21", "2026-12-28", 4), ("2026-12-28", "2026-12-28", 0), ("2026-01-01", "2027-01-01", 254),
    ("2027-12-01", "2028-01-10", -1),
])
def test_business_days_between(de, start, end, answer):
    assert de.business_days_between("DE", start, end) == answer


def test_a_year_nobody_imported_is_unknown(bd):
    assert bd.is_business_day("FR", "2026-07-14") == "unknown"
    assert bd.add_business_days("FR", "2026-07-13", 1) == ""
    assert bd.business_days_between("FR", "2026-07-13", "2026-07-20") == -1


@pytest.mark.parametrize("call, reason", [
    (lambda c: c.is_business_day("DE", "2026-02-30"), "day must be a date"),
    (lambda c: c.add_business_days("DE", "2026-12-23", 0), "n must be from 1 to 260"),
    (lambda c: c.add_business_days("DE", "2026-12-23", 261), "n must be from 1 to 260"),
    (lambda c: c.business_days_between("DE", "2026-12-28", "2026-12-21"), "end must be on or after start"),
    (lambda c: c.business_days_between("DE", "2026-01-01", "2029-12-31"), "at most three years"),
    (lambda c: c.holidays("Germany", 2026), "two-letter ISO"),
])
def test_views_refuse_bad_input(direct_vm, de, call, reason):
    with direct_vm.expect_revert(reason):
        call(de)
