"""
llm.py
All Gemini calls live here. Gemini is used ONLY for things that genuinely
need language reasoning:
  - structuring raw scraped JD text into title/company/skills/responsibilities/qualifications
  - writing strengths & weaknesses narrative
  - improving resume bullets
  - generating interview questions
  - company-specific feedback (grounded in computed fit scores)
  - section-specific resume rewrite (new: experience / skills / projects)

It is NOT used to invent the ATS score or skill-match numbers — those
come from matcher.py / ats.py.
"""

import os
import json
import re
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"


def _get_model():
    return genai.GenerativeModel(MODEL_NAME)


def _safe_json_parse(raw: str):
    """Strip markdown code fences if present and parse JSON."""
    cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def structure_job_description(raw_jd_text: str) -> dict:
    """Turn raw scraped/pasted JD text into structured fields."""
    prompt = f"""You are extracting structured fields from a job posting.
Return ONLY valid JSON, no markdown, no commentary, with exactly these keys:
{{
  "job_title": string,
  "company": string,
  "skills": [list of specific technical skills/tools mentioned],
  "responsibilities": [list of short bullet strings],
  "qualifications": [list of short bullet strings]
}}

Job posting text:
\"\"\"{raw_jd_text[:8000]}\"\"\"
"""
    response = _get_model().generate_content(prompt)
    parsed = _safe_json_parse(response.text)
    if parsed is None:
        return {
            "job_title": "Unknown",
            "company": "Unknown",
            "skills": [],
            "responsibilities": [],
            "qualifications": [],
            "_raw_error": response.text,
        }
    return parsed


def generate_strengths_weaknesses(resume_text: str, jd_text: str, ats_result: dict) -> dict:
    """Narrative strengths/weaknesses grounded in the computed match data."""
    prompt = f"""You are a technical recruiter. Based on the resume and job
description below, AND the computed match data, list:
- 3-5 concise strengths (each under 12 words)
- 3-5 concise weaknesses/gaps (each under 12 words)

Return ONLY valid JSON: {{"strengths": [...], "weaknesses": [...]}}

Computed matched skills: {ats_result['keyword_gap']['matched']}
Computed missing skills: {ats_result['keyword_gap']['missing']}

Resume:
\"\"\"{resume_text[:6000]}\"\"\"

Job Description:
\"\"\"{jd_text[:4000]}\"\"\"
"""
    response = _get_model().generate_content(prompt)
    parsed = _safe_json_parse(response.text)
    if parsed is None:
        return {"strengths": [], "weaknesses": [], "_raw_error": response.text}
    return parsed


def improve_bullet(bullet_text: str, jd_text: str) -> str:
    """Rewrite a single resume bullet to be stronger / more JD-aligned."""
    prompt = f"""Rewrite this single resume bullet point to be more impactful:
use a strong action verb, add quantifiable impact if plausible, and align
language with the target job description where honest to do so. Do NOT
invent numbers/metrics that aren't implied by the original bullet — if no
metric is implied, improve the verb/clarity instead. Return ONLY the
rewritten bullet text, nothing else.

Original bullet: "{bullet_text}"

Target job description (for tone/keyword alignment only):
\"\"\"{jd_text[:2000]}\"\"\"
"""
    response = _get_model().generate_content(prompt)
    return response.text.strip().strip('"')


def generate_company_specific_feedback(resume_text: str, jd_text: str,
                                       ats_result: dict, company_profile: dict,
                                       company_fit: dict) -> str:
    """
    Phase 2: feedback that accounts for a specific company's known hiring priorities.
    Now receives the pre-computed company_fit dict so it references real numbers.
    """
    prompt = f"""You are a recruiter who specializes in hiring for {company_profile['name'].title()}.
Given the resume, job description, and computed match data below, write a short
(120-180 word) piece of feedback tailored to how {company_profile['name'].title()}
specifically evaluates candidates. Reference their actual priority skills and
culture/interview style where relevant. Be direct and specific, not generic.

{company_profile['name'].title()}'s known priority skills: {company_profile['priority_skills']}
{company_profile['name'].title()}'s culture/interview notes: {company_profile['culture_notes']}
{company_profile['name'].title()}'s leveling notes: {company_profile['leveling_hint']}

Candidate has these company priority skills: {company_fit['matched_priority']}
Candidate is missing these company priority skills: {company_fit['missing_priority']}
Company fit score (priority skills only): {company_fit['fit_score']}%

Computed matched skills: {ats_result['keyword_gap']['matched']}
Computed missing skills: {ats_result['keyword_gap']['missing']}
Overall computed ATS score: {ats_result['overall']}%

Resume:
\"\"\"{resume_text[:5000]}\"\"\"

Job Description:
\"\"\"{jd_text[:3000]}\"\"\"
"""
    response = _get_model().generate_content(prompt)
    return response.text.strip()


def suggest_similar_jobs(jd_structured: dict) -> dict:
    """
    Phase 3: 'Similar Job Recommendations' — given a structured JD, suggest
    comparable roles at other companies. LLM judgment grounded in its training
    knowledge — treat as discovery starting points, not verified live postings.
    """
    prompt = f"""Given this job posting, suggest 5 comparable roles at OTHER
companies that a candidate could also apply to. Return ONLY valid JSON:
{{"similar_roles": [{{"company": string, "role_title": string, "why_similar": string}}]}}

Job Title: {jd_structured.get('job_title')}
Company: {jd_structured.get('company')}
Skills: {jd_structured.get('skills')}
Responsibilities: {jd_structured.get('responsibilities')}
"""
    response = _get_model().generate_content(prompt)
    parsed = _safe_json_parse(response.text)
    if parsed is None:
        return {"similar_roles": [], "_raw_error": response.text}
    return parsed


def rewrite_resume_section(resume_text: str, jd_text: str,
                            section_name: str, section_content: str,
                            missing_skills: list) -> str:
    """
    Phase 3 improvement: rewrite a specific section of the resume (Experience,
    Skills, or Projects) rather than the whole document. More practical for
    targeted improvements. section_name: 'experience' | 'skills' | 'projects'
    """
    section_display = section_name.title()
    prompt = f"""Rewrite only the '{section_display}' section of this resume to
be more impactful and better aligned with the target job description.

Rules:
- Do NOT invent companies, titles, dates, metrics, or skills not already mentioned.
- Improve verbs, clarity, structure, and foreground JD-relevant content.
- For Skills section: reorganize to surface the most JD-relevant skills first.
- For Experience/Projects: tighten bullet points using strong action verbs.
- At the end, add one short paragraph labeled "Suggested Additions (verify before using):"
  mentioning any missing skills from the list below that the candidate should add
  if they genuinely have that experience. Do NOT add them into the main section body.
- Return only the rewritten section in clean Markdown, starting with ## {section_display}.

Missing skills to note as suggestions: {missing_skills}

Current '{section_display}' section:
\"\"\"{section_content[:4000]}\"\"\"

Target job description (for alignment):
\"\"\"{jd_text[:2500]}\"\"\"

Full resume context (read-only, for coherence):
\"\"\"{resume_text[:4000]}\"\"\"
"""
    response = _get_model().generate_content(prompt)
    return response.text.strip()


def rewrite_resume(resume_text: str, jd_text: str, missing_skills: list) -> str:
    """
    Phase 3: 'Resume Rewrite' — full resume rewrite. Kept for backward compat.
    Prefer rewrite_resume_section for targeted rewrites.
    """
    prompt = f"""Rewrite the following resume to be more impactful and better
aligned with the target job description. Rules:
- Do NOT invent companies, titles, dates, metrics, or skills the person
  doesn't already mention.
- You MAY improve verbs, clarity, and structure, and reorder bullets to
  foreground JD-relevant experience.
- For each skill in the "missing skills" list below, add one line at the
  end under "## Suggested Additions (verify before using)" noting that the
  candidate should add a project/line item if they genuinely have that
  experience — do NOT add it directly into the resume body.
- Return the rewritten resume in clean Markdown.

Missing skills (JD wants these, not currently evidenced in resume): {missing_skills}

Original resume:
\"\"\"{resume_text[:7000]}\"\"\"

Target job description:
\"\"\"{jd_text[:3000]}\"\"\"
"""
    response = _get_model().generate_content(prompt)
    return response.text.strip()


def generate_interview_questions(resume_text: str, jd_text: str) -> dict:
    """Phase 2 feature: interview question generator."""
    prompt = f"""Based on this resume and job description, generate interview
questions a candidate should prepare for. Return ONLY valid JSON:
{{"hr_questions": [...], "technical_questions": [...], "project_questions": [...]}}
3-5 questions per category.

Resume:
\"\"\"{resume_text[:6000]}\"\"\"

Job Description:
\"\"\"{jd_text[:4000]}\"\"\"
"""
    response = _get_model().generate_content(prompt)
    parsed = _safe_json_parse(response.text)
    if parsed is None:
        return {"hr_questions": [], "technical_questions": [], "project_questions": [],
                "_raw_error": response.text}
    return parsed
