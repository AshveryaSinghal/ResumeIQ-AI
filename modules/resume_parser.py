"""
resume_parser.py
Extracts full text from a resume PDF (not just page 1 as an image)
and splits it into rough sections: Education, Experience, Skills,
Projects, Achievements.
"""

import re
import pdfplumber


SECTION_HEADERS = {
    "education": ["education", "academic background", "academics"],
    "experience": ["experience", "work experience", "internship", "internships",
                   "professional experience", "employment"],
    "skills": ["skills", "technical skills", "skill set", "core competencies"],
    "projects": ["projects", "academic projects", "personal projects"],
    "achievements": ["achievements", "awards", "honors", "accomplishments",
                      "certifications", "extra curricular", "extracurricular"],
}


def extract_text(uploaded_file) -> str:
    """Extract full text from every page of the resume PDF."""
    uploaded_file.seek(0)
    text_chunks = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)


def split_into_sections(full_text: str) -> dict:
    """
    Very lightweight section splitter. Looks for lines that are likely
    headers (short, mostly capitalized / matches known header keywords)
    and buckets the text under them.
    """
    lines = [l.strip() for l in full_text.split("\n") if l.strip()]
    sections = {key: [] for key in SECTION_HEADERS}
    sections["other"] = []

    current_section = "other"

    for line in lines:
        lowered = line.lower().strip(":")
        matched = None
        for section, keywords in SECTION_HEADERS.items():
            # treat as a header only if short line and matches a keyword closely
            if len(lowered) <= 40:
                for kw in keywords:
                    if lowered == kw or lowered.startswith(kw):
                        matched = section
                        break
            if matched:
                break

        if matched:
            current_section = matched
            continue  # don't include the header line itself

        sections[current_section].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def estimate_experience_months(full_text: str) -> int:
    """
    Rough heuristic: looks for date ranges like 'Jan 2026 - Mar 2026' or
    '06/2025 - 08/2025' or 'X months' / 'X years' mentions and sums them.
    This is intentionally simple — good enough to drive the eligibility
    checker, not meant to be a precise HR-grade calculator.
    """
    months_found = 0

    # Pattern: "X months" or "X-month"
    for m in re.finditer(r"(\d+)\s*[\-]?\s*months?", full_text, re.IGNORECASE):
        months_found += int(m.group(1))

    # Pattern: "X years"
    for m in re.finditer(r"(\d+)\s*[\-]?\s*years?", full_text, re.IGNORECASE):
        months_found += int(m.group(1)) * 12

    # Pattern: Month Year - Month Year (date ranges, common in resumes)
    month_names = (r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                   r"[a-z]*\.?\s+\d{4}")
    range_pattern = rf"({month_names})\s*[-–to]+\s*({month_names}|Present|present|Current|current)"
    import datetime
    for m in re.finditer(range_pattern, full_text):
        try:
            start = datetime.datetime.strptime(re.sub(r"[a-z]*\.?", "", m.group(1)).strip(), "%b %Y") \
                if False else _parse_month_year(m.group(1))
            end_raw = m.group(2)
            end = datetime.datetime.now() if end_raw.lower() in ("present", "current") \
                else _parse_month_year(end_raw)
            if start and end and end >= start:
                delta_months = (end.year - start.year) * 12 + (end.month - start.month)
                months_found += max(delta_months, 0)
        except Exception:
            continue

    return months_found


def _parse_month_year(text):
    import datetime
    text = text.strip()
    for fmt in ("%b %Y", "%B %Y", "%b. %Y"):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None
