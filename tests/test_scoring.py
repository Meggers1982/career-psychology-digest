import scoring


def test_the_evidence_ladder_is_io_psychologys():
    cases = {
        "A meta-analysis of 212 effect sizes": "meta-analysis",
        "A field experiment at a call center": "field experiment",
        "A quasi-experimental study of a mentoring program": "field experiment",
        "A three-wave longitudinal study of new hires": "longitudinal",
        "A daily diary study over ten workdays": "experience sampling",
        "An experience sampling design with 120 nurses": "experience sampling",
        "Personnel records for 48,200 employees": "archival data",
        "An experimental vignette study of hiring managers": "experimental vignette",
        "Across four studies, participants were randomly assigned": "experiments",
        "A scale development and validation study": "large-sample survey",
        "Supervisor-rated performance in a multisource survey": "large-sample survey",
        "A cross-sectional self-report survey of 412 employees": "cross-sectional self-report",
        "A questionnaire of 300 respondents": "survey",
        "In-depth interviews with 22 managers": "qualitative",
        "A systematic review of the burnout literature": "review",
    }
    for text, label in cases.items():
        assert scoring.evidence_type(text)[0] == label, text


def test_the_ladder_orders_designs_by_causal_strength():
    points = lambda t: scoring.evidence_type(t)[1]
    assert points("meta-analysis") == points("field experiment") == 5
    assert points("longitudinal study") > points("experimental vignette study")
    assert points("experimental vignette study") > points("cross-sectional self-report survey")
    assert points("cross-sectional self-report survey") < scoring.evidence_type("Researchers found a link.")[1]


def test_a_longitudinal_survey_is_not_scored_as_cross_sectional():
    assert scoring.evidence_type("A two-wave survey of employees")[0] == "longitudinal"


def test_an_unstated_design_is_neutral():
    assert scoring.evidence_type("Researchers found a link.") == ("unspecified", 2)


def test_a_field_experiment_outranks_a_survey():
    assert scoring.evidence_type("field experiment")[1] > scoring.evidence_type("survey")[1]


def test_sample_size_reads_the_forms_write_ups_use():
    assert scoring.sample_size("N = 1,204 employees")[0] == 1204
    assert scoring.sample_size("data from 48,200 workers")[0] == 48200
    assert scoring.sample_size("1,150 job applicants")[0] == 1150
    assert scoring.sample_size("3.1 million workers")[0] == 3_100_000
    assert scoring.sample_size("no numbers here") == (None, 2)


def test_recency_reads_iso_dates():
    assert scoring.recency("2026-09-02", "2026-09-14") == 5
    assert scoring.recency("2026-05-02", "2026-09-14") == 3
    assert scoring.recency("", "2026-09-14") == 0
    assert scoring.recency("2026-11-01", "2026-09-14") == 5   # issue date ahead


def test_an_unmeasured_component_is_dropped_not_guessed():
    assert scoring.story_score({"evidence_type": 5, "coverage_gap": None}) == 100


def test_an_unchecked_study_cannot_be_a_lead():
    study = {"the_study": "A field experiment with 48,200 employees.",
             "journal": "Journal of Applied Psychology", "published": "2026-09-10"}
    unchecked = scoring.score_study(study, run_date="2026-09-14", verdict="accurate")
    assert unchecked["score"] >= 82
    assert unchecked["band"] == "Strong"
    checked = scoring.score_study(study, run_date="2026-09-14",
                                  coverage_state="unreported", verdict="accurate")
    assert checked["band"] == "Lead"


def test_verdicts_are_the_records_words():
    assert scoring.accuracy("accurate") == 5
    assert scoring.accuracy("significant") == 0
    assert scoring.accuracy(None) is None


def test_journal_tier_uses_the_ratings():
    top = scoring.score_study({"journal": "Journal of Applied Psychology"}, run_date="2026-09-14")
    assert top["journal_tier"] == "A*"
    assert top["components"]["journal_tier"] == 5


def test_blank_ratings_degrade_gracefully():
    # Personnel Psychology has ABDC/AJG but a core journal with none is "core".
    core = scoring.score_study({"journal": "Journal of Occupational and Organizational Psychology"},
                               run_date="2026-09-14")
    assert core["journal_tier"] == "core"
    assert core["components"]["journal_tier"] == 4
    other = scoring.score_study({"journal": "Some Unlisted Journal"}, run_date="2026-09-14")
    assert other["journal_tier"] == "unknown"
    assert other["components"]["journal_tier"] == 3
