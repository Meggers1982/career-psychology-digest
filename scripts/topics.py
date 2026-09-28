"""The rotation's topics: what each one searches for, and how studies get tagged.

One place for both, so a renamed topic cannot split a beat in two -- the bug
senior-research-digest hit when "fall prevention" became "falls" mid-archive
and trends.py stopped finding the run before it.

`QUERIES` are OpenAlex boolean title-and-abstract searches (AND / OR / quoted
phrases; OpenAlex stems, so "brand" also finds "brands"). `TAG_TERMS` are
lowercase substrings matched against the finished write-up, so a study found
on a hiring day that is really about bias carries both tags.
"""
from __future__ import annotations

BROAD = ""
BROAD_LABEL = "Broad (all career and work psychology topics)"

# Every query is anchored to a workplace term so it stays on industrial/
# organizational psychology and off general or clinical psychology.
QUERIES = {
    "leadership & management": (
        '(leader OR leadership OR manager OR supervisor OR "middle management") AND '
        '(employee OR workplace OR organization OR subordinate OR team OR follower) AND '
        '("leadership style" OR "transformational leadership" OR "servant leadership" OR '
        '"abusive supervision" OR "psychological safety" OR "management practice" OR '
        'feedback OR "trust in leader" OR "leader behavior")'
    ),
    "workplace stress & burnout": (
        '(burnout OR "job stress" OR "occupational stress" OR "work stress" OR '
        '"emotional exhaustion" OR "job demands" OR overwork OR "workplace incivility" OR '
        '"work overload" OR "psychological detachment") AND '
        '(employee OR worker OR job OR workplace OR occupational)'
    ),
    "career development & mobility": (
        '("career development" OR "career success" OR "career transition" OR '
        '"career adaptability" OR "career mobility" OR promotion OR "job crafting" OR '
        '"career change" OR "career plateau" OR mentoring OR "job search" OR '
        '"upward mobility" OR "professional development" OR "turnover intention")'
    ),
    "hiring & selection": (
        '("personnel selection" OR "employee selection" OR "job interview" OR '
        '"hiring decision" OR recruitment OR recruiter OR "applicant" OR "resume" OR '
        '"cognitive ability test" OR "structured interview" OR "hiring bias" OR '
        '"job applicant" OR onboarding OR "employer brand")'
    ),
    "remote & hybrid work": (
        '("remote work" OR telework OR telecommuting OR "hybrid work" OR '
        '"work from home" OR "virtual work" OR "flexible work" OR "return to office" OR '
        '"virtual team" OR "flexible working" OR "distributed work")'
    ),
    "motivation & engagement": (
        '("work motivation" OR "employee engagement" OR "job satisfaction" OR '
        '"organizational commitment" OR "intrinsic motivation" OR "job performance" OR '
        '"goal setting" OR "meaningful work" OR "job autonomy" OR "employee recognition" OR '
        '"organizational citizenship" OR "work engagement" OR "employee retention")'
    ),
    "team dynamics & collaboration": (
        '("team performance" OR "team effectiveness" OR "team cohesion" OR '
        '"team conflict" OR "team diversity" OR "team collaboration" OR '
        '"teamwork" OR "workplace conflict" OR "coworker" OR "team cognition" OR '
        '"group performance" OR "cross-functional team")'
    ),
    "diversity, equity & inclusion at work": (
        '(diversity OR inclusion OR discrimination OR bias OR "pay gap" OR "glass ceiling" OR '
        '"gender gap" OR harassment OR "belonging" OR microaggression) AND '
        '(workplace OR employee OR organization OR hiring OR leadership OR career OR workforce)'
    ),
    "negotiation & decision-making": (
        '(negotiation OR negotiator OR "managerial decision" OR "organizational decision" OR '
        '"decision making" OR "group decision" OR "judgment bias") AND '
        '(workplace OR manager OR employee OR organization OR business OR "salary" OR '
        'executive OR firm)'
    ),
    "entrepreneurship": (
        '(entrepreneur OR entrepreneurship OR founder OR "start-up" OR startup OR '
        '"new venture" OR "self-employment" OR "small business owner" OR intrapreneur) AND '
        '(personality OR motivation OR psychological OR cognition OR wellbeing OR "well-being" OR '
        'identity OR resilience OR failure OR passion OR behavior)'
    ),
    "workplace communication": (
        '("workplace communication" OR "organizational communication" OR "employee voice" OR '
        '"speaking up" OR "feedback seeking" OR "email overload" OR "meeting" OR '
        '"internal communication" OR "virtual communication" OR "workplace conversation" OR '
        '"whistleblowing" OR "silence in organizations" OR "workplace gossip")'
    ),
    "ai & the future of work": (
        '("artificial intelligence" OR "generative AI" OR automation OR algorithm OR '
        'ChatGPT OR "large language model" OR robot OR "algorithmic management" OR '
        '"machine learning") AND '
        '(employee OR worker OR workplace OR job OR "future of work" OR occupation OR '
        'manager OR "human resource" OR workforce)'
    ),
    "compensation": (
        '(compensation OR salary OR "pay satisfaction" OR "pay transparency" OR '
        '"pay equity" OR bonus OR "incentive pay" OR "executive pay" OR "wage" OR '
        '"pay for performance" OR "employee benefits" OR "pay raise") AND '
        '(employee OR worker OR organization OR employer OR firm OR workplace OR job)'
    ),
    "wellbeing & work-life balance": (
        '("work-life balance" OR "work-family conflict" OR "work-life conflict" OR '
        '"work-life" OR "employee wellbeing" OR "employee well-being" OR "four-day week" OR '
        '"family-supportive" OR "boundary management" OR "always-on" OR '
        '"recovery from work" OR "occupational health") '
    ),
}

DEFAULT_ROTATION = [BROAD, *QUERIES]

TAG_TERMS = {
    "leadership & management": ("leader", "manager", "managerial", "supervisor",
                                "psychological safety", "management"),
    "workplace stress & burnout": ("burnout", "job stress", "work stress", "occupational stress",
                                   "exhaustion", "job demands", "incivility", "overwork"),
    "career development & mobility": ("career", "promotion", "mentor", "job search",
                                      "job crafting", "turnover", "upward mobility"),
    "hiring & selection": ("hiring", "recruit", "selection", "applicant", "interview",
                           "resume", "onboarding"),
    "remote & hybrid work": ("remote work", "telework", "hybrid work", "work from home",
                             "telecommut", "flexible work", "return to office", "virtual team"),
    "motivation & engagement": ("motivation", "engagement", "job satisfaction", "commitment",
                                "job performance", "meaningful work", "retention", "autonomy"),
    "team dynamics & collaboration": ("team", "coworker", "collaborat", "group performance",
                                      "workplace conflict"),
    "diversity, equity & inclusion at work": ("diversity", "inclusion", "discriminat",
                                              "pay gap", "gender gap", "glass ceiling",
                                              "harassment", "belonging", "microaggression"),
    "negotiation & decision-making": ("negotiat", "decision making", "decision-making",
                                      "judgment", "managerial decision"),
    "entrepreneurship": ("entrepreneur", "founder", "start-up", "startup", "new venture",
                         "self-employ", "small business"),
    "workplace communication": ("communication", "employee voice", "speaking up",
                                "feedback seeking", "meeting", "whistleblow"),
    "ai & the future of work": ("artificial intelligence", " ai ", "ai-", "generative",
                                "automation", "algorithm", "machine learning", "robot",
                                "language model", "future of work"),
    "compensation": ("compensation", "salary", "salaries", "pay transparency", "pay equity",
                     "pay satisfaction", "bonus", "incentive pay", "wage", "benefits"),
    "wellbeing & work-life balance": ("work-life", "work-family", "wellbeing", "well-being",
                                      "four-day", "boundary", "recovery from work",
                                      "occupational health"),
}

# str.title() capitalizes small words and mangles acronyms; fix them here.
_LABEL_FIXES = (("Ai ", "AI "), (" The ", " the "), (" At ", " at "), (" Of ", " of "))

TOPIC_ALIASES: dict[str, str] = {}


def normalize_topic(topic: str) -> str:
    """Canonical name for a topic, whatever the rotation called it at the time."""
    cleaned = " ".join((topic or "").split()).lower()
    return TOPIC_ALIASES.get(cleaned, cleaned)


def query_for(topic: str) -> str:
    """The OpenAlex search for a topic. A topic with no entry here -- a one-off
    typed into the workflow_dispatch box -- is searched as a plain phrase."""
    key = normalize_topic(topic)
    if not key:
        return ""
    return QUERIES.get(key) or f'"{topic.strip()}"'


def label_for(topic: str) -> str:
    key = normalize_topic(topic)
    if not key:
        return BROAD_LABEL
    label = key.title()
    for old, new in _LABEL_FIXES:
        label = label.replace(old, new)
    return label


def tags_for(text: str, topic: str = "") -> list[str]:
    blob = f" {(text or '').lower()} "
    tags = {tag for tag, terms in TAG_TERMS.items() if any(t in blob for t in terms)}
    if normalize_topic(topic):
        tags.add(normalize_topic(topic))
    return sorted(tags)
