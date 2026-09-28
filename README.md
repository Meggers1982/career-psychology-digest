# Career Psychology Digest

A daily research digest on industrial/organizational psychology as it applies to career, work, and business. It is not a general or clinical psychology digest. Modeled on `marketing-research-digest`.

## How it works

1. **Search.** `scripts/openalex.py` queries OpenAlex for recent articles from the journals in `config/journals.csv`, using the day's topic from `config/digest_config.json` (`scripts/topics.py` holds the queries).
2. **Screen.** `scripts/screening.py` drops non-research, missing abstracts, off-topic and clinical-only articles, anything already covered, and applies the per-journal and total caps.
3. **Score.** `scripts/scoring.py` ranks by study design (meta-analyses and field experiments high, cross-sectional self-report low), sample size, journal tier, and recency.
4. **Write.** `scripts/digest_generator.py` has Claude write the digest.
5. **Fact-check.** `scripts/fact_checker.py` re-reads each abstract against what the digest says.
6. **Coverage and trends.** `scripts/web_coverage.py` checks whether the press has covered each study; `scripts/trends.py` compares against the last digest on the topic and drafts pitch ideas.
7. **Dashboard.** `scripts/build_dashboard_data.py` writes `docs/data/`, and `docs/index.html` renders it. Vercel serves `docs/`.

The workflow in `.github/workflows/daily-digest.yml` runs the tests, then the pipeline, then commits the run back to `main`.

## Secrets (GitHub Actions)

| Secret | Required | Used for |
|---|---|---|
| `ANTHROPIC_API_KEY` | yes | digest, fact-check, trends |
| `SERPAPI_API_KEY` | no | press-coverage check |
| `OPENALEX_API_KEY` | no | higher OpenAlex rate limit |

Commits must come from the Meggers1982 no-reply address, or Vercel Hobby blocks the deploy on a private repo.

## Where this differs from marketing-research-digest

- Topics rotate through work and career themes (leadership, burnout, hiring, remote work, and so on).
- The evidence ladder is tuned for I-O designs, and a cross-sectional self-report study scores below an unspecified design because of common-method bias.
- Core I-O and career journals are trusted on topic; other journals must mention work terms and are dropped if they read as clinical.
- Journal tiers (FT50, ABDC, AJG) in `config/journals.csv` were entered from memory for 16 journals and left blank elsewhere. Verify before relying on them. Blank rows are neutral, and core I-O journals get a small category lift.
- Fact-check and framing prompts target WEIRD/MTurk samples generalized to "workers", causal claims from self-report data, and single-company samples.

## Changing things

- **Topics:** edit `focus_rotation` in `config/digest_config.json` and the matching entries in `scripts/topics.py`. Set `subject_focus` to pin one topic.
- **Journals:** edit `config/journals.csv`, then run `python scripts/resolve_sources.py` to refresh the OpenAlex IDs.
- **Manual run:** trigger the workflow with `workflow_dispatch` and an optional focus.

## Running locally

    pip install -r requirements.txt pytest
    python -m pytest tests/ -q          # no API calls
    cd scripts && ANTHROPIC_API_KEY=... python main.py

Use Python 3.11 and set `SSL_CERT_FILE` if you hit SSL errors.
