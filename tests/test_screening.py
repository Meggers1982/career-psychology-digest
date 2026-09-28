import json
from datetime import date

import journals
import screening

JMR = journals.find("Journal of Applied Psychology")      # core I-O, trusted
AI_SOC = journals.find("Human Resource Management")      # not core: needs a work term
LONG = "employees " + "x " * 300


def work(wid, source, title="A study of employee pay", abstract=LONG, type_="article",
         published="2026-09-01", doi=""):
    return {"work_id": wid, "source_id": source.source_id if source else "",
            "journal": source.name if source else "", "title": title, "abstract": abstract,
            "type": type_, "published": published, "doi": doi, "relevance": None}


def test_fixture_journals_exist():
    assert JMR and JMR.source_id and screening.is_trusted(JMR)
    assert AI_SOC and AI_SOC.source_id and not screening.is_trusted(AI_SOC)
    assert not screening.is_trusted(None)


def test_front_matter_and_non_articles_are_dropped(tmp_path):
    works = [work("W1", JMR, title="Editorial: the year ahead"),
             work("W2", JMR, type_="erratum"),
             work("W3", JMR, title="Corrigendum to X"),
             work("W4", JMR)]
    chosen, counts = screening.select(works, tmp_path, today=date(2026, 9, 14))
    assert [w["work_id"] for w in chosen] == ["W4"]
    assert counts["not_research"] == 3


def test_an_article_without_an_abstract_cannot_be_considered(tmp_path):
    chosen, counts = screening.select([work("W1", JMR, abstract="")], tmp_path)
    assert not chosen and counts["no_abstract"] == 1


def test_other_journals_must_mention_work(tmp_path):
    off = work("W1", AI_SOC, title="Ontology of robots", abstract="philosophy " * 100)
    on = work("W2", AI_SOC, title="Chatbots and employee trust", abstract=LONG)
    chosen, counts = screening.select([off, on], tmp_path)
    assert [w["work_id"] for w in chosen] == ["W2"]
    assert counts["off_topic"] == 1


def test_the_core_journals_are_trusted_on_topic(tmp_path):
    chosen, _ = screening.select([work("W1", JMR, abstract="philosophy " * 100)], tmp_path)
    assert len(chosen) == 1


def test_clinical_only_articles_drop_even_in_a_core_journal(tmp_path):
    clinical = work("W1", JMR, title="CBT for adolescents",
                    abstract="patients with major depression received therapy " * 20)
    occupational = work("W2", JMR, title="Burnout",
                        abstract="patients with depression among employees and nurses " * 20)
    chosen, counts = screening.select([clinical, occupational], tmp_path)
    assert [w["work_id"] for w in chosen] == ["W2"]
    assert counts["off_topic"] == 1


def test_clinical_articles_with_one_stray_work_word_drop_elsewhere(tmp_path):
    stray = work("W1", AI_SOC, title="Therapy outcomes",
                 abstract="patients in psychotherapy improved; one clinician job " * 20)
    chosen, counts = screening.select([stray], tmp_path)
    assert not chosen and counts["off_topic"] == 1


def test_a_study_written_up_before_is_not_pitched_again(tmp_path):
    (tmp_path / "earlier.json").write_text(json.dumps({
        "run_date": "2026-09-01",
        "studies": [{"work_id": "W1", "doi": "10.1/a"}]}))
    works = [work("W1", JMR), work("W2", JMR, doi="10.1/A"), work("W3", JMR)]
    chosen, counts = screening.select(works, tmp_path)
    # W2 matches on DOI, case-insensitively.
    assert [w["work_id"] for w in chosen] == ["W3"]
    assert counts["already_covered"] == 2


def test_one_journal_cannot_fill_the_run(tmp_path):
    works = [work(f"W{i}", JMR) for i in range(10)]
    chosen, counts = screening.select(works, tmp_path, max_per_journal=3)
    assert len(chosen) == 3
    assert counts["over_journal_cap"] == 7


def test_the_cap_holds_and_every_article_is_accounted_for(tmp_path):
    many = [journals.find(n) for n in (
        "Journal of Applied Psychology", "Personnel Psychology", "Journal of Vocational Behavior",
        "Journal of Organizational Behavior", "Organizational Behavior and Human Decision Processes")]
    works = [work(f"W{j}{i}", source) for j, source in enumerate(many) for i in range(5)]
    works.append(work("Wx", JMR, abstract=""))
    chosen, counts = screening.select(works, tmp_path, max_abstracts=8, max_per_journal=3)
    assert len(chosen) == counts["sent"] == 8
    dropped = sum(v for k, v in counts.items() if k not in {"found", "sent"})
    assert counts["found"] == counts["sent"] + dropped


def test_higher_rated_and_newer_articles_rank_first(tmp_path):
    c_rated = journals.find("Career Development International")
    works = [work("Wold", c_rated, published="2026-07-20"),
             work("Wnew", JMR, published="2026-09-10")]
    chosen, _ = screening.select(works, tmp_path, today=date(2026, 9, 14))
    assert [w["work_id"] for w in chosen] == ["Wnew", "Wold"]


def test_very_long_abstracts_are_trimmed_for_the_prompt(tmp_path):
    chosen, _ = screening.select([work("W1", JMR, abstract="word " * 2000)], tmp_path)
    assert len(chosen[0]["abstract"]) <= screening.MAX_ABSTRACT_CHARS + 2
