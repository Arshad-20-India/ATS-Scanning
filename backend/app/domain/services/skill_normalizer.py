"""
Deterministic skill-name normalization.

Skill matching is intentionally NOT done via embeddings: "JS" and
"JavaScript" are the same skill with 100% certainty, and treating that
as a fuzzy semantic-similarity problem would introduce needless
uncertainty into what should be an exact, auditable check. Embeddings
are reserved for genuinely ambiguous judgments (is this bullet relevant
to this requirement?), not for alias resolution, which is a solved,
deterministic problem given a good taxonomy.

The alias table here is intentionally small and illustrative. In
production this would be loaded from a maintained skills taxonomy
(e.g. a versioned JSON/DB table) rather than hardcoded, but the
normalization *algorithm* stays the same regardless of table size.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

_DEFAULT_ALIASES: Dict[str, str] = {
    # Tech & Software
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "postgres": "postgresql",
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node": "node.js",
    "cicd": "ci/cd",
    "ci-cd": "ci/cd",
    "nextjs": "next.js",
    "vuejs": "vue",
    "vue.js": "vue",
    "expressjs": "express.js",
    "express": "express.js",
    "rest": "rest api",
    "restful": "rest api",
    "restful api": "rest api",
    "mongo": "mongodb",
    "tailwind": "tailwindcss",
    "html": "html5",
    "css": "css3",

    # Marketing & Growth
    "sem": "search engine marketing",
    "seo": "search engine optimization",
    "ga": "google analytics",
    "ga4": "google analytics",
    "crm": "customer relationship management",
    "cro": "conversion rate optimization",
    "roas": "return on ad spend",
    "cac": "customer acquisition cost",
    "ltv": "lifetime value",

    # Healthcare & Nursing
    "rn": "registered nurse",
    "bsn": "bachelor of science in nursing",
    "ehr": "electronic health records",
    "emr": "electronic medical records",
    "cpr": "cardiopulmonary resuscitation",
    "bls": "basic life support",
    "acls": "advanced cardiovascular life support",
    "icu": "intensive care unit",
    "er": "emergency room",

    # Finance & Accounting
    "m&a": "mergers and acquisitions",
    "p&l": "profit and loss",
    "cfa": "chartered financial analyst",
    "cpa": "certified public accountant",
    "roi": "return on investment",
    "kpi": "key performance indicator",
    "dcf": "discounted cash flow",
    "fp&a": "financial planning and analysis",

    # Business & Operations
    "pm": "project management",
    "pmp": "project management professional",
    "agile": "agile methodology",
    "scrum": "scrum methodology",
    "sop": "standard operating procedures",
    "okr": "objectives and key results",
}


class SkillNormalizer:
    def __init__(self, aliases: Optional[Dict[str, str]] = None) -> None:
        self._aliases = {**_DEFAULT_ALIASES, **(aliases or {})}

    def normalize(self, raw_skill: str) -> str:
        """
        Lowercase, strip punctuation noise, collapse whitespace, then
        resolve through the alias table. Deterministic and pure —
        same input always yields same output.
        """
        cleaned = raw_skill.strip().lower()
        cleaned = re.sub(r"[()\[\]{}]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return self._aliases.get(cleaned, cleaned)
