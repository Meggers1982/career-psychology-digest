import journals


def test_issns_survive_what_a_spreadsheet_does_to_them():
    assert journals.normalize_issn("0022-2429") == "0022-2429"
    assert journals.normalize_issn("09732586") == "0973-2586"
    assert journals.normalize_issn("9732594") == "0973-2594"
    assert journals.normalize_issn("1234-567x") == "1234-567X"


def test_placeholders_are_not_issns():
    for raw in ("", "unverified", "n/a", "N/A (online only)", "-"):
        assert journals.normalize_issn(raw) == "", raw


def test_ceased_and_dormant_titles_are_not_searched():
    active_names = {j.name for j in journals.active()}
    everything = journals.load()
    inactive = [j for j in everything if not j.active]
    assert all(j.name not in active_names for j in inactive)


def test_most_active_journals_resolve_to_an_openalex_source():
    """ A big drop means the CSV lost its
    source-ID column (re-run resolve_sources.py), not that journals vanished."""
    assert len(journals.searchable()) >= 40


def test_tier_comes_from_the_lists_own_ratings():
    jap = journals.find("Journal of Applied Psychology")
    assert journals.tier_points(jap) == ("A*", 5)
    assert journals.tier_points(journals.find("Personnel Psychology")) == ("A*", 5)
    assert journals.tier_points(None) == ("unknown", 3)


def test_ft50_membership_alone_makes_a_journal_elite():
    ft50 = {j.name for j in journals.load() if j.ft50}
    assert {"Journal of Applied Psychology", "Academy of Management Journal"} <= ft50


def test_a_blank_rating_is_neutral_and_core_journals_get_a_small_lift():
    joop = journals.find("Journal of Occupational and Organizational Psychology")
    assert not (joop.abdc or joop.ajg or joop.ft50)
    assert journals.tier_points(joop) == ("core", 4)
    blank_non_core = journals.find("Human Resource Management")
    assert journals.tier_points(blank_non_core) == ("unrated", 3)


def test_ft50_no_is_not_a_penalty():
    assert journals.find("Leadership Quarterly").ft50 is False
    assert journals.tier_points(journals.find("Leadership Quarterly"))[0] == "A*"


def test_find_tolerates_case_and_a_leading_the():
    assert journals.find("the journal of applied psychology") is not None
    assert journals.find("JOURNAL OF APPLIED PSYCHOLOGY").name == "Journal of Applied Psychology"
