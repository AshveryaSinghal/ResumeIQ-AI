"""
ats.py
Computes a real, explainable ATS compatibility score from weighted
sub-scores instead of asking the LLM to invent a percentage.

Overall ATS = weighted average of:
  - Skill match (matched skills / JD skills)        weight 0.40
  - Semantic/keyword text similarity (TF-IDF)        weight 0.25
  - Experience match (meets JD's stated requirement) weight 0.20
  - Section completeness (education/exp/skills/etc.) weight 0.15

BUG FIX: compute_ats_score now accepts jd_structured_skills so that
skill matching uses BOTH the raw JD text AND the LLM-structured skills
list. This prevents the 100% skill match / matched=[] contradiction.
"""

from . import matcher


SECTION_WEIGHTS = {
    "education": 0.25,
    "experience": 0.30,
    "skills": 0.25,
    "projects": 0.20,
}


def section_completeness_score(sections: dict) -> float:
    """0-100 score based on which expected sections were found and non-trivial."""
    score = 0.0
    for section, weight in SECTION_WEIGHTS.items():
        content = sections.get(section, "")
        if len(content.strip()) > 20:
            score += weight
    return round(score * 100, 2)


def experience_match_score(required_years, candidate_months) -> float:
    """
    If the JD doesn't state a required experience, treat as fully satisfied
    (no penalty for not finding a number we can't be sure about).
    """
    if required_years is None:
        return 100.0
    required_months = required_years * 12
    if candidate_months >= required_months:
        return 100.0
    if candidate_months <= 0:
        return 0.0
    return round((candidate_months / required_months) * 100, 2)


def skill_match_score(gap: dict) -> float:
    if gap["jd_skill_count"] == 0:
        # If truly no skills found in the JD, return 50 (unknown, not perfect)
        return 50.0
    return round((len(gap["matched"]) / gap["jd_skill_count"]) * 100, 2)


def compute_ats_score(resume_text: str, jd_text: str, sections: dict,
                      candidate_months_experience: int,
                      jd_structured_skills: list = None) -> dict:
    """
    jd_structured_skills: list of skill strings from LLM structured extraction.
    Pass this in so skill matching uses both raw text AND structured LLM output.
    """
    gap = matcher.keyword_gap(resume_text, jd_text,
                               jd_structured_skills=jd_structured_skills)
    required_years = matcher.extract_required_experience_years(jd_text)

    skill_score = skill_match_score(gap)
    similarity_score = matcher.text_similarity(resume_text, jd_text)
    exp_score = experience_match_score(required_years, candidate_months_experience)
    section_score = section_completeness_score(sections)

    overall = (
        skill_score * 0.40
        + similarity_score * 0.25
        + exp_score * 0.20
        + section_score * 0.15
    )

    return {
        "overall": round(overall, 2),
        "breakdown": {
            "skill_match": skill_score,
            "text_similarity": similarity_score,
            "experience_match": exp_score,
            "section_completeness": section_score,
        },
        "keyword_gap": gap,
        "required_years": required_years,
        "candidate_months_experience": candidate_months_experience,
    }


def compare_resumes(resume_versions: list, jd_text: str, sections_list: list,
                    months_list: list, jd_structured_skills: list = None) -> list:
    """
    Phase 3: 'Multi Resume Comparison' — run the same JD against several
    resume versions and return their scores side by side.
    """
    results = []
    for label_text, sections, months in zip(resume_versions, sections_list, months_list):
        label, resume_text = label_text
        result = compute_ats_score(resume_text, jd_text, sections, months,
                                   jd_structured_skills=jd_structured_skills)
        results.append({"label": label, **result})
    return results


def compare_jds(resume_text: str, jd_versions: list, sections: dict,
                months: int) -> list:
    """
    Phase 3: 'Multi JD Comparison' — run one resume against several job
    descriptions to see which one it matches best.
    """
    results = []
    for label, jd_text in jd_versions:
        result = compute_ats_score(resume_text, jd_text, sections, months)
        results.append({"label": label, **result})
    return sorted(results, key=lambda r: r["overall"], reverse=True)


def check_eligibility(required_years, candidate_months_experience: int) -> dict:
    """
    Phase 1 'Eligibility Checker' feature: does the candidate meet the
    stated experience bar in the JD?
    """
    if required_years is None:
        return {
            "eligible": True,
            "reason": "No explicit minimum experience requirement was detected "
                      "in this job posting.",
            "recommendation": None,
        }

    required_months = required_years * 12
    if candidate_months_experience >= required_months:
        return {
            "eligible": True,
            "reason": f"Role requires {required_years}+ year(s); your resume "
                      f"shows roughly {candidate_months_experience} month(s) "
                      f"of relevant experience.",
            "recommendation": None,
        }

    gap_months = required_months - candidate_months_experience
    return {
        "eligible": False,
        "reason": f"Role requires {required_years}+ year(s) of experience; "
                  f"your resume shows roughly {candidate_months_experience} "
                  f"month(s) — about {gap_months} month(s) short.",
        "recommendation": "Look for the 'New Grad' / 'Entry Level' / 'Intern' "
                          "version of this role, or roles explicitly open to "
                          "students/0-1 YOE.",
    }


def compute_company_fit(resume_text: str, company_profile: dict) -> dict:
    """
    Phase 2 improvement: compute a measurable company fit score based on
    the company's known priority skills, instead of purely relying on LLM.
    Returns matched_priority, missing_priority, and a fit_score (0-100).
    """
    resume_skills = matcher.extract_skills(resume_text)
    priority = [s.lower() for s in company_profile.get("priority_skills", [])]

    matched = [s for s in priority if s in resume_skills]
    missing = [s for s in priority if s not in resume_skills]

    fit_score = round((len(matched) / len(priority)) * 100, 1) if priority else 0.0

    return {
        "matched_priority": matched,
        "missing_priority": missing,
        "fit_score": fit_score,
        "total_priority_skills": len(priority),
    }
