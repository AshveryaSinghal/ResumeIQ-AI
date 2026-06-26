# 🎯 ResumeIQ AI — AI Career Copilot

> AI-powered resume analysis that gives you a **real, explainable ATS score** — not an LLM-guessed number.

---

## ✨ Features

| Feature | Description |
|---|---|
| **ATS Score** | Weighted formula: skill match + TF-IDF similarity + experience + section completeness |
| **Eligibility Check** | Regex-extracts "X+ years" from the JD; tells you if you qualify and what to do if not |
| **Keyword Gap Analysis** | Matched / missing / extra skills with color-coded tags |
| **Strengths & Weaknesses** | Gemini narrative grounded in the computed gap (not hallucinated) |
| **Bullet Improver** | Rewrites a single resume bullet with stronger verbs — no fabricated metrics |
| **Company Fit** | Curated profiles for 15+ top tech companies (Amazon, Google, Meta, Microsoft, Stripe…) |
| **Interview Prep** | HR / Technical / Project-based questions generated for your specific resume + JD |
| **Skill Roadmap** | Deterministic week-by-week learning plan ordered by difficulty heuristic |
| **Section Rewrite** | AI rewrites Experience / Skills / Projects — never invents experience |
| **PDF Report** | One-click downloadable report with score table, keyword gap, roadmap |
| **Dashboard** | KPI cards, score history chart, breakdown progress bars (requires login) |
| **Resume Version Tracker** | Every parsed resume auto-saved; compare versions side-by-side |
| **Multi-JD Comparison** | Paste 2–5 JDs to see which role your resume matches best |
| **Similar Job Recommendations** | AI suggests comparable roles at other companies |
| **Auth** | bcrypt-hashed signup/login; guest mode for quick use |

---

## 🖥 Screenshots

> _Add screenshots here once deployed. Suggested shots: Analysis tab (score cards + keyword gap), Dashboard (KPI cards + history chart), Company Fit page, Roadmap._

---

## 🏗 Architecture

```
resumeiq/
├── app.py                   # Streamlit UI — all tabs and sidebar
├── requirements.txt
├── .env                     # GOOGLE_API_KEY=...
├── resumeiq.db              # SQLite, auto-created on first run
└── modules/
    ├── jd_extractor.py      # Fetch + clean text from a job posting URL
    ├── resume_parser.py     # PDF text extraction, section splitter, experience estimator
    ├── skills_db.py         # ~200 known skills, aliases, category map
    ├── matcher.py           # Skill extraction (regex + alias), TF-IDF similarity, keyword gap
    ├── ats.py               # Weighted ATS score, eligibility, company fit, multi-resume/JD compare
    ├── llm.py               # All Gemini calls (structure JD, narrative, rewrites, questions)
    ├── storage.py           # SQLite: users, resume versions, analysis history
    ├── auth.py              # bcrypt signup/login
    ├── company_profiles.py  # Curated hiring-priority profiles for 15+ companies
    ├── roadmap.py           # Deterministic week-by-week skill roadmap
    └── report.py            # PDF report generation (reportlab)
```

---

## 🧮 How the ATS Score is Computed

```
Overall ATS = 0.40 × skill_match
            + 0.25 × text_similarity  (TF-IDF cosine)
            + 0.20 × experience_match
            + 0.15 × section_completeness
```

All four sub-scores are computed deterministically from your resume and JD — **no LLM is asked to invent a number**. Gemini is used only for language tasks (structuring text, writing narratives, generating questions).

Tune the weights in `ats.py → compute_ats_score()`.

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| AI | Google Gemini 2.5 Flash |
| Skill matching | Regex + alias resolution + TF-IDF (scikit-learn) |
| PDF parsing | pdfplumber |
| PDF generation | reportlab |
| Charts | Plotly |
| Auth | bcrypt |
| Database | SQLite |
| JD scraping | requests + BeautifulSoup4 |

---

## 🚀 Installation

```bash
# 1. Clone
git clone https://github.com/your-username/resumeiq.git
cd resumeiq

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Gemini API key
echo "GOOGLE_API_KEY=your_key_here" > .env

# 4. Run
streamlit run app.py
```

A `resumeiq.db` SQLite file is created automatically on first run — no separate database setup needed.

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com).

---

## 🗺 Roadmap / Future Improvements

- [ ] Semantic skill matching with `sentence-transformers` (upgrade from TF-IDF)
- [ ] spaCy `PhraseMatcher` NER for dynamic skill ontology (upgrade from fixed keyword list)
- [ ] Live job board integration (LinkedIn, Greenhouse) for verified Similar Roles
- [ ] Resume scoring history export (CSV)
- [ ] Multi-language resume support
- [ ] Chrome extension for one-click JD capture
- [ ] PostgreSQL backend for multi-user production deployment

---

## ⚠️ Known Limitations

- **Skill extraction is a fixed keyword list**, not NER — may miss unusual framings.
- **Text similarity is TF-IDF**, not semantic embeddings — can score poorly on paraphrased matches.
- **Experience estimation is regex** — works for `Mon YYYY – Mon YYYY` formats; unusual layouts may misfire.
- **JD link fetching fails** on JS-heavy / login-walled pages (LinkedIn, Workday) — use "Paste JD text" instead.
- **Company profiles are curated**, not scraped — 15 companies currently; add more in `company_profiles.py`.
- **Similar Job Recommendations** are LLM judgment, not verified live postings.
- **SQLite** is fine for personal/portfolio use; swap to PostgreSQL for real multi-user production.

