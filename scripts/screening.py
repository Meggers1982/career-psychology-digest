"""Choose which articles the model sees.

OpenAlex hands back everything the journals published in the window --
editorials, errata, calls for papers, and (in the wider management, HR and
health journals) a good deal that is not about work at all. The model is capped at MAX_ABSTRACTS a run,
so what fills those slots is decided here, cheaply and deterministically, and
every drop is counted so the dashboard can say what the run did not consider.

In order:

1. **Not research** -- OpenAlex types other than article/review, and titles that
   announce front matter ("Editorial", "Erratum", "Call for papers").
2. **No abstract** -- nothing to write up or fact-check against. Mostly Elsevier;
   see openalex.py.
3. **Off-topic** -- the core I-O and career journals are trusted to be
   on-beat; every other journal's articles must mention a work or career term.
   In all journals, articles that read as clinical or general psychology (patients,
   therapy, children, psychiatric conditions) with no work vocabulary are dropped.
4. **Already written up** -- any work ID or DOI a previous digest covered. The
   window is wider than a day and runs are daily, so without this the same
   article would be pitched again and again (new-scientist-story-ideas' PMID
   ledger, derived here from the archive instead of kept as a second file).
5. **Rank and cap** -- journal tier, recency and (on topic days) OpenAlex's
   relevance, with at most MAX_PER_JOURNAL from any one journal so one prolific
   title cannot fill the run.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import journals as journals_mod

KEEP_TYPES = {"article", "review"}

FRONT_MATTER = re.compile(
    r"^\s*(editorial|erratum|errata|corrigendum|correction|retraction|retracted|"
    r"call for papers|introduction to (the )?special issue|guest editorial|"
    r"reviewer acknowledg|book review|in memoriam|obituary|editor'?s note|"
    r"from the editor|commentary on|reply to|response to|expression of concern)",
    re.I,
)

MIN_ABSTRACT_CHARS = 400
MAX_ABSTRACT_CHARS = 3500

WORK_TERMS = re.compile(
    r"employee|worker|workplace|work-?place|workforce|\bjobs?\b|\bwork (?:engagement|stress|"
    r"demands|hours|role|environment|performance|attitudes|design)|career|occupation|vocation|"
    r"organi[sz]ation|organi[sz]ational|manager|managerial|supervisor|leader|leadership|"
    r"\bteams?\b|coworker|colleague|\bHR\b|human resource|hiring|recruit|personnel selection|employee selection|selection (?:process|procedure|interview)|"
    r"applicant|candidate|personnel|staffing|turnover|retention|burnout|work engagement|employee engagement|"
    r"onboarding|promotion (?:decision|opportunit)|mentor|telework|remote work|hybrid work|unemploy|"
    r"entrepreneur|talent|\bpay\b|wage|salary|compensation|"
    r"performance (?:appraisal|review|evaluation|management)|job satisfaction|"
    r"work-family|work-life",
    re.I,
)

# Clinical / general psychology vocabulary. An article that uses these and no
# work vocabulary is off the beat even in a trusted journal (Journal of
# Occupational Health Psychology and Applied Psychology carry some of both).
CLINICAL_TERMS = re.compile(
    r"patients?\b|psychotherap|clinical (?:trial|sample|population|intervention)|"
    r"psychiatr|schizophreni|bipolar|depressive disorder|major depression|anxiety disorder|"
    r"\bptsd\b|post-?traumatic|autism|\badhd\b|dementia|eating disorder|"
    r"suicid|children|adolescen|infant|toddler|preschool|"
    r"cognitive behaviou?ral therapy|\btherapy\b|neuroimaging|\bfmri\b|rodent",
    re.I,
)


def is_research(work: dict) -> bool:
    return work.get("type") in KEEP_TYPES and not FRONT_MATTER.match(work.get("title") or "")


def is_trusted(journal: journals_mod.Journal | None) -> bool:
    """The core I-O psychology and career journals (Elite I-O Psychology,
    Career & Vocational Psychology) are on-beat by definition. Every other
    listed journal, and any unlisted one, must show a work term."""
    return journals_mod.is_core(journal)


def on_topic(work: dict, journal: journals_mod.Journal | None) -> bool:
    text = f"{work.get('title', '')} {work.get('abstract', '')}"
    has_work = bool(WORK_TERMS.search(text))
    if is_trusted(journal):
        # Trusted, but clinical/general-psychology-only work still drops.
        return has_work or not CLINICAL_TERMS.search(text)
    return has_work and not (CLINICAL_TERMS.search(text) and len({m.group(0).lower() for m in WORK_TERMS.finditer(text)}) < 2)


def covered_before(outputs_dir: Path) -> set[str]:
    """Every work ID and DOI a previous digest wrote up, lowercased."""
    seen = set()
    for path in outputs_dir.glob("*.json"):
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for study in run.get("studies") or []:
            for key in (study.get("work_id"), study.get("doi")):
                if key and str(key).lower() not in {"not available", ""}:
                    seen.add(str(key).lower())
    return seen


def _recency_points(published: str, today: date) -> float:
    try:
        days = (today - date.fromisoformat(published[:10])).days
    except ValueError:
        return 0.0
    if days <= 14:
        return 2.0
    if days <= 30:
        return 1.5
    if days <= 60:
        return 1.0
    return 0.5


def priority(work: dict, journal: journals_mod.Journal | None, today: date,
             max_relevance: float) -> float:
    _, tier = journals_mod.tier_points(journal)
    relevance = 0.0
    if max_relevance and work.get("relevance"):
        relevance = 2.0 * float(work["relevance"]) / max_relevance
    return tier + _recency_points(work.get("published") or "", today) + relevance


def select(
    works: list[dict],
    outputs_dir: Path,
    max_abstracts: int = 40,
    max_per_journal: int = 3,
    today: date | None = None,
) -> tuple[list[dict], dict]:
    """(chosen works, counts of what was dropped and why)."""
    today = today or date.today()
    by_source = journals_mod.by_source_id()
    already = covered_before(outputs_dir)

    counts = {"found": len(works), "not_research": 0, "no_abstract": 0,
              "off_topic": 0, "already_covered": 0, "over_journal_cap": 0,
              "over_cap": 0, "sent": 0}
    eligible = []
    for work in works:
        if not is_research(work):
            counts["not_research"] += 1
            continue
        if len(work.get("abstract") or "") < MIN_ABSTRACT_CHARS:
            counts["no_abstract"] += 1
            continue
        journal = by_source.get(work.get("source_id", ""))
        if not on_topic(work, journal):
            counts["off_topic"] += 1
            continue
        keys = {str(work.get("work_id", "")).lower(), str(work.get("doi", "")).lower()} - {""}
        if keys & already:
            counts["already_covered"] += 1
            continue
        eligible.append((work, journal))

    max_relevance = max((float(w.get("relevance") or 0) for w, _ in eligible), default=0.0)
    eligible.sort(key=lambda pair: (
        -priority(pair[0], pair[1], today, max_relevance),
        pair[0].get("published") or "",
    ))

    chosen, per_journal = [], {}
    for work, _ in eligible:
        source = work.get("source_id") or work.get("journal")
        if per_journal.get(source, 0) >= max_per_journal:
            counts["over_journal_cap"] += 1
            continue
        if len(chosen) >= max_abstracts:
            counts["over_cap"] += 1
            continue
        per_journal[source] = per_journal.get(source, 0) + 1
        trimmed = dict(work)
        if len(trimmed["abstract"]) > MAX_ABSTRACT_CHARS:
            trimmed["abstract"] = trimmed["abstract"][:MAX_ABSTRACT_CHARS].rsplit(" ", 1)[0] + " …"
        chosen.append(trimmed)
    counts["sent"] = len(chosen)
    return chosen, counts
