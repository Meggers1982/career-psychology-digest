# Career Psychology Digest

Work in progress. A daily research digest on I-O and organizational psychology as it applies to career, work, and business, modeled on `marketing-research-digest` (OpenAlex, screen, Claude-written digest, self fact-check, static dashboard).

## What's here so far

- `config/journals.csv`: 42 journals (I-O psychology, career development, HR/management) with OpenAlex source IDs matched.
- `scripts/openalex.py`, `scripts/journals.py`, `scripts/resolve_sources.py`: ported from marketing-research-digest.
- `scripts/build_journals_csv.py`: one-off script that generated the journal list.

## What's left

Tracked in the Linear project "Career Psychology Digest" (MEA-972 to MEA-983): topic rotation, scoring ladder, remaining pipeline scripts, dashboard, tests, workflow and secrets, Vercel, failure-alert monitoring.

## Working on another machine

    git clone git@github.com:Meggers1982/career-psychology-digest.git

Re-run `python scripts/resolve_sources.py` after changing the journal list (use python3.11 with `SSL_CERT_FILE` set if you hit SSL errors).
