"""
roadmap.py
Generates a week-by-week learning roadmap from missing skills.

Improvements:
  - Better difficulty scoring based on category
  - Always produces a roadmap (falls back to company priorities then general recommendations)
  - Resource hints per skill type
  - Priority tags (High / Medium / Low)
"""

DIFFICULTY_HINTS = {
    # Easy (1-2 weeks)
    "git": 1, "github": 1, "html": 1, "css": 1, "markdown": 1,
    "bash": 2, "linux": 2, "sql": 2, "excel": 1, "figma": 2,
    "agile": 1, "scrum": 1, "jira": 1,
    # Medium (2-3 weeks)
    "rest api": 2, "graphql": 2, "rest": 2, "api design": 2,
    "data structures": 3, "algorithms": 3,
    "unit testing": 2, "pytest": 2, "jest": 2,
    "docker": 3, "github actions": 2, "ci/cd": 3,
    "react": 3, "node.js": 3, "fastapi": 2, "flask": 2, "django": 3,
    "postgresql": 2, "mongodb": 2, "redis": 2,
    "machine learning": 4, "scikit-learn": 3, "pandas": 2, "numpy": 2,
    "ownership": 2, "leadership": 2,
    # Hard (4+ weeks)
    "kubernetes": 5, "terraform": 4, "ansible": 4,
    "aws": 4, "azure": 4, "gcp": 4, "google cloud": 4,
    "kafka": 4, "spark": 5, "hadoop": 5, "airflow": 4,
    "deep learning": 5, "pytorch": 4, "tensorflow": 4,
    "nlp": 4, "computer vision": 5, "llm": 4, "rag": 4,
    "system design": 5, "distributed systems": 5, "scalability": 4,
    "microservices": 4, "kubernetes": 5,
    "prompt engineering": 3, "langchain": 3,
}

RESOURCE_HINTS = {
    "docker": "docs.docker.com + 'Docker in a Weekend' tutorial",
    "kubernetes": "kubernetes.io/docs + KodeKloud free tier",
    "aws": "AWS Skill Builder free courses + AWS Cloud Practitioner",
    "azure": "Microsoft Learn (free) + AZ-900 certification",
    "gcp": "Google Cloud Skills Boost + Associate Cloud Engineer path",
    "system design": "'Designing Data-Intensive Applications' by Kleppmann",
    "data structures": "LeetCode Top Interview 150 + NeetCode roadmap",
    "algorithms": "LeetCode Top Interview 150 + NeetCode roadmap",
    "machine learning": "fast.ai Practical ML course (free) + Kaggle",
    "deep learning": "fast.ai Deep Learning course + PyTorch tutorials",
    "react": "react.dev official docs + Build a project on Vercel",
    "sql": "SQLZoo + Mode Analytics SQL Tutorial (both free)",
    "git": "git-scm.com Book (free) + GitHub Learning Lab",
    "ci/cd": "GitHub Actions docs + build a pipeline for a side project",
    "kafka": "Confluent Kafka 101 free course + build a producer-consumer",
    "langchain": "LangChain docs + build a simple RAG chatbot",
    "llm": "Andrej Karpathy's 'Neural Networks Zero to Hero' on YouTube",
    "prompt engineering": "OpenAI Prompt Engineering guide + Anthropic cookbook",
    "rag": "LangChain RAG tutorial + vector DB quickstart (Chroma/Pinecone)",
}

GENERAL_FALLBACK_SKILLS = [
    {"skill": "system design", "reason": "Essential for senior engineering roles"},
    {"skill": "docker", "reason": "Industry-standard containerisation"},
    {"skill": "aws", "reason": "Most in-demand cloud platform"},
    {"skill": "ci/cd", "reason": "Expected in all production workflows"},
    {"skill": "data structures", "reason": "Core technical interview requirement"},
    {"skill": "algorithms", "reason": "Core technical interview requirement"},
]


def _difficulty(skill: str) -> int:
    return DIFFICULTY_HINTS.get(skill.lower(), 3)


def _priority_label(skill: str, idx: int, total: int) -> str:
    if idx < total * 0.33:
        return "High"
    if idx < total * 0.66:
        return "Medium"
    return "Low"


def build_roadmap(
    missing_skills: list,
    total_weeks: int = 8,
    company_missing_priority: list = None,
) -> list:
    """
    Build a week-by-week learning roadmap.

    Priority:
    1. JD missing skills (sorted by difficulty: easy first)
    2. Company priority skills the candidate lacks
    3. General high-value skills (fallback so roadmap is never empty)
    """
    source = list(missing_skills) if missing_skills else []
    source_label = ""

    if not source and company_missing_priority:
        source = list(company_missing_priority)
        source_label = "Company priority: "

    if not source:
        # Absolute fallback — always give the user something actionable
        source = [item["skill"] for item in GENERAL_FALLBACK_SKILLS]
        source_label = "Recommended: "

    # Sort by difficulty (easiest first for quick wins)
    ordered = sorted(source, key=_difficulty)
    total = len(ordered)

    weeks = []
    week_num = 1
    i = 0

    while i < len(ordered) and week_num <= total_weeks:
        skill = ordered[i]
        difficulty = _difficulty(skill)

        # Hard skills get their own week; easier skills can be batched
        if difficulty >= 4:
            batch = [skill]
            i += 1
        elif difficulty == 3:
            batch = ordered[i:i + 2]
            i += 2
        else:
            batch = ordered[i:i + 3]
            i += 3

        # Remove None entries if batch went past end
        batch = [s for s in batch if s]
        priority = _priority_label(skill, week_num - 1, total)

        resource = next(
            (RESOURCE_HINTS[s.lower()] for s in batch if s.lower() in RESOURCE_HINTS),
            "Search for an official quickstart tutorial and build a mini project.",
        )

        weeks.append({
            "week": week_num,
            "skills": batch,
            "priority": priority,
            "focus": f"Build a small hands-on project using {', '.join(batch)}.",
            "resource": resource,
            "label": source_label + ", ".join(batch),
        })
        week_num += 1

    # If there are remaining skills beyond total_weeks, append to last week
    if i < len(ordered) and weeks:
        weeks[-1]["skills"].extend(ordered[i:])

    return weeks
