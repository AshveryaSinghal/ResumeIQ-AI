"""
matcher.py
Production-grade matching logic — no LLM guessing numbers.

Improvements over v1:
  - Alias / synonym resolution before matching
  - Category-aware extraction
  - Removes single-letter false positives (was matching 'c' and 'r')
  - Better tokenization with word boundary checks
  - Accepts jd_structured_skills to prevent 0-skill JD edge case
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skills_db import SKILLS_LOWER_SET, SKILL_ALIASES, SKILL_CATEGORIES


# ── Normalisation helpers ──────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Lowercase and collapse whitespace."""
    return re.sub(r"\s+", " ", text.lower().strip())


def _resolve_alias(skill: str) -> str:
    """Map a raw skill string to its canonical form via the alias table."""
    return SKILL_ALIASES.get(skill.lower(), skill.lower())


# ── Core skill extractor ───────────────────────────────────────────────────

def extract_skills(text: str) -> set:
    """
    Return the subset of known skills that appear in `text`.

    Improvements:
    - Skip single-character 'skills' (blocks 'c', 'r', 'go' ambiguities
      except where explicitly mapped as multi-char aliases).
    - Use word-boundary regex so 'java' doesn't match inside 'javascript'.
    - Resolve aliases so alternate spellings merge to canonical forms.
    """
    norm = _normalize(text)
    found = set()

    # First pass: alias substitution in normalised text for common short forms
    for alias, canonical in SKILL_ALIASES.items():
        if len(alias) <= 2:
            # Only replace if it's a standalone token
            if re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", norm):
                # Add canonical, don't replace in text (avoids cascading subs)
                if canonical in SKILLS_LOWER_SET:
                    found.add(canonical)

    # Second pass: scan all known skills against normalized text
    for skill in SKILLS_LOWER_SET:
        # Skip ambiguous single-char skills ('c', 'r') — handled via context
        if len(skill) <= 1:
            continue
        # 'go' is special: only match as standalone word, not inside 'ago', 'django', etc.
        pattern = r"(?<![a-zA-Z0-9\-\.])" + re.escape(skill) + r"(?![a-zA-Z0-9\-\.])"
        if re.search(pattern, norm):
            found.add(skill)

    # Handle 'c' programming language specifically — only if context suggests it
    c_lang_patterns = [
        r"\bc\s+programming\b", r"\bc\s+language\b", r"\bin\s+c\b",
        r"\bc\s+code\b", r"\bc/c\+\+", r"\bc\s+developer\b",
        r"proficient in c\b", r"experience in c\b",
    ]
    for p in c_lang_patterns:
        if re.search(p, norm):
            found.add("c")
            break

    return found


def normalize_skill_list(raw_skills: list) -> set:
    """
    Normalize LLM-extracted skill strings into canonical lowercase known skills.
    Uses alias resolution + partial matching as fallback.
    """
    result = set()
    for raw in raw_skills:
        norm = _normalize(raw)
        # Try alias resolution first
        canonical = _resolve_alias(norm)
        if canonical in SKILLS_LOWER_SET:
            result.add(canonical)
            continue
        # Direct match
        if norm in SKILLS_LOWER_SET:
            result.add(norm)
            continue
        # Partial: a known skill is contained in raw or vice versa (min 4 chars)
        for known in SKILLS_LOWER_SET:
            if len(known) >= 4 and (known in norm or norm in known):
                result.add(known)
                break
    return result


# ── Keyword gap analysis ───────────────────────────────────────────────────

def keyword_gap(resume_text: str, jd_text: str,
                jd_structured_skills: list = None) -> dict:
    """
    Compare skills found in resume vs JD.

    Merges regex-extracted skills with LLM-structured skills to prevent
    the 0-skill JD edge case (which previously caused 100% match with 0 matched).
    """
    resume_skills = extract_skills(resume_text)
    jd_skills_regex = extract_skills(jd_text)

    if jd_structured_skills:
        jd_skills_structured = normalize_skill_list(jd_structured_skills)
        jd_skills = jd_skills_regex | jd_skills_structured
    else:
        jd_skills = jd_skills_regex

    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)
    extra = sorted(resume_skills - jd_skills)

    return {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "jd_skill_count": len(jd_skills),
        "resume_skill_count": len(resume_skills),
    }


# ── Text similarity ────────────────────────────────────────────────────────

def text_similarity(resume_text: str, jd_text: str) -> float:
    """
    TF-IDF cosine similarity (0-100).

    Upgrade path: swap in sentence-transformers all-MiniLM-L6-v2 for
    true semantic similarity without changing the API.
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=8000,
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
    )
    try:
        tfidf = vectorizer.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    except ValueError:
        return 0.0
    return round(float(sim) * 100, 2)


# ── Experience extraction ─────────────────────────────────────────────────

def extract_required_experience_years(jd_text: str):
    """
    Parse minimum experience requirement from JD text.
    Returns the minimum years found, or None.
    """
    patterns = [
        r"(\d+)\s*\+\s*years?",
        r"minimum\s+(?:of\s+)?(\d+)\s*years?",
        r"at\s+least\s+(\d+)\s*years?",
        r"(\d+)\s*-\s*\d+\s*years?\s+(?:of\s+)?experience",
        r"(\d+)\s*years?\s+of\s+(?:relevant\s+)?experience",
        r"(\d+)\s*years?\s+(?:minimum|required)",
    ]
    found_years = []
    for p in patterns:
        for m in re.finditer(p, jd_text, re.IGNORECASE):
            val = int(m.group(1))
            if 0 < val <= 25:  # sanity guard
                found_years.append(val)
    return min(found_years) if found_years else None


# ── Category breakdown ────────────────────────────────────────────────────

def categorize_skills(skills: set) -> dict:
    """Group a flat set of skills into their named categories for display."""
    result = {}
    for category, cat_skills in SKILL_CATEGORIES.items():
        cat_set = set(s.lower() for s in cat_skills)
        hits = sorted(skills & cat_set)
        if hits:
            result[category] = hits
    return result
