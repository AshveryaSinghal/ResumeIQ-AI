"""
company_profiles.py
Curated hiring profiles for major tech companies.
Each profile drives the measurable Company Fit score (computed in ats.py)
and provides LLM context for qualitative feedback.

Expanded to 15+ companies with richer priority skill lists.
"""

COMPANY_PROFILES = {
    "amazon": {
        "priority_skills": [
            "aws", "system design", "data structures", "algorithms",
            "scalability", "java", "python", "distributed systems",
            "microservices", "ci/cd", "ownership",
        ],
        "culture_notes": (
            "Amazon evaluates heavily against its Leadership Principles — "
            "Ownership, Customer Obsession, Dive Deep, Deliver Results. "
            "Technical rounds focus on DS/Algo + System Design. "
            "STAR-format answers are expected for behavioral rounds."
        ),
        "leveling_hint": (
            "Distinct SDE Internship / New Grad (SDE-I) vs experienced SDE-II/III tracks. "
            "Experience bar is strictly enforced."
        ),
        "hiring_focus": "Backend, distributed systems, AWS-native services, leadership bar.",
    },
    "microsoft": {
        "priority_skills": [
            "c#", ".net", "azure", "system design", "data structures",
            "algorithms", "python", "typescript", "react", "sql",
        ],
        "culture_notes": (
            "Microsoft emphasizes Growth Mindset and collaborative problem solving. "
            "Interviews include coding rounds (DS/Algo), a design round, and a "
            "culture-fit interview. Azure knowledge is a strong differentiator."
        ),
        "leveling_hint": (
            "University hire tracks (Explore, New Grad) are separate from experienced SWE. "
            "SDET/SWE/PM roles have distinct pipelines."
        ),
        "hiring_focus": "Full-stack, Azure cloud, productivity tools, AI integration.",
    },
    "google": {
        "priority_skills": [
            "data structures", "algorithms", "system design", "distributed systems",
            "python", "c++", "java", "go", "scalability", "machine learning",
        ],
        "culture_notes": (
            "Google interviews are algorithm-heavy — 4-5 Leetcode-style rounds "
            "plus a Googleyness + Leadership round. Strong CS fundamentals are "
            "the primary bar. Published research or open-source work helps for L5+."
        ),
        "leveling_hint": (
            "L3 (new grad) vs L4/L5 (experienced) distinction is important. "
            "APM program has its own track."
        ),
        "hiring_focus": "Infrastructure, ML systems, search, ads, cloud (GCP).",
    },
    "meta": {
        "priority_skills": [
            "data structures", "algorithms", "system design", "react",
            "python", "php", "c++", "product sense", "ml",
        ],
        "culture_notes": (
            "Meta values speed of execution and measurable impact. Interviews "
            "include 2 coding rounds, 1 system design, and 1 behavioral on past "
            "impact. Product sense is evaluated for non-infra roles."
        ),
        "leveling_hint": (
            "E3 (new grad) vs E4/E5 (experienced). IC roles vs management track diverge early."
        ),
        "hiring_focus": "Social platforms, VR/AR (Reality Labs), ads infrastructure, AI research.",
    },
    "stripe": {
        "priority_skills": [
            "ruby", "python", "go", "distributed systems", "api design",
            "system design", "postgresql", "typescript", "node.js",
        ],
        "culture_notes": (
            "Stripe leans toward strong generalists with high code quality and "
            "clear written communication. Values pragmatic API design, "
            "attention to detail, and engineering craft."
        ),
        "leveling_hint": (
            "Smaller new-grad intake than big tech; typically expects internship/project "
            "depth even for entry-level roles."
        ),
        "hiring_focus": "Payments infrastructure, financial APIs, developer tooling.",
    },
    "atlassian": {
        "priority_skills": [
            "java", "python", "react", "typescript", "node.js",
            "aws", "kubernetes", "system design", "agile", "jira",
        ],
        "culture_notes": (
            "Atlassian values team culture ('TEAM Anywhere') and balanced engineering. "
            "Interviews include coding, system design, and values-alignment rounds. "
            "Strong focus on collaboration and async communication."
        ),
        "leveling_hint": "Associate vs Senior SWE tracks; remote-first culture globally.",
        "hiring_focus": "Developer tools, project management, team collaboration platforms.",
    },
    "adobe": {
        "priority_skills": [
            "c++", "python", "java", "machine learning", "computer vision",
            "react", "typescript", "cloud", "aws", "system design",
        ],
        "culture_notes": (
            "Adobe focuses on creativity + engineering. Roles span creative AI "
            "(Firefly, Sensei), cloud infrastructure, and enterprise SaaS. "
            "ML and CV experience is highly valued."
        ),
        "leveling_hint": "University hire programs distinct from experienced roles; L1–L5 levels.",
        "hiring_focus": "Creative AI, document cloud, digital marketing, enterprise SaaS.",
    },
    "salesforce": {
        "priority_skills": [
            "java", "javascript", "apex", "lightning web components",
            "salesforce platform", "sql", "aws", "system design",
            "rest api", "agile",
        ],
        "culture_notes": (
            "Salesforce values platform knowledge alongside core CS skills. "
            "Trailhead/Salesforce certification is a differentiator. "
            "Strong emphasis on customer success and collaborative culture."
        ),
        "leveling_hint": "AMTS (Associate MTS) new grad vs MTS/SMTS experienced tracks.",
        "hiring_focus": "CRM platform, Slack integration, marketing cloud, AI/Einstein features.",
    },
    "datadog": {
        "priority_skills": [
            "go", "python", "java", "distributed systems", "kafka",
            "kubernetes", "prometheus", "grafana", "aws", "system design",
        ],
        "culture_notes": (
            "Datadog is engineering-heavy and product-led. Interviews focus on "
            "backend systems, observability, and real-world problem solving. "
            "Experience with metrics/logging pipelines is a strong signal."
        ),
        "leveling_hint": "Competitive compensation; fast-growth company with flat structure.",
        "hiring_focus": "Observability, APM, infrastructure monitoring, security.",
    },
    "uber": {
        "priority_skills": [
            "python", "java", "go", "system design", "distributed systems",
            "kafka", "spark", "sql", "machine learning", "kubernetes",
        ],
        "culture_notes": (
            "Uber values 'say it as it is' culture with strong ownership. "
            "Technical bar is high: DS/Algo + complex system design problems. "
            "Experience with real-time systems and data pipelines is prized."
        ),
        "leveling_hint": "L3–L7 levels; new grad starts at L3/L4.",
        "hiring_focus": "Marketplace technology, maps, driver/rider platforms, ML infra.",
    },
    "snowflake": {
        "priority_skills": [
            "sql", "python", "java", "c++", "distributed systems",
            "data engineering", "aws", "azure", "system design", "dbt",
        ],
        "culture_notes": (
            "Snowflake is data-cloud focused. Engineers work on large-scale "
            "query processing, storage optimization, and customer data platforms. "
            "Strong SQL and distributed systems knowledge is essential."
        ),
        "leveling_hint": "IC1–IC5 levels; competitive equity packages.",
        "hiring_focus": "Cloud data platform, query optimization, data sharing, ML features.",
    },
    "servicenow": {
        "priority_skills": [
            "java", "javascript", "python", "sql", "rest api",
            "system design", "aws", "agile", "microservices",
        ],
        "culture_notes": (
            "ServiceNow focuses on enterprise IT workflows and digital transformation. "
            "Platform knowledge is valued; interviews are moderate DS/Algo "
            "with strong emphasis on practical system design."
        ),
        "leveling_hint": "IC1–IC6 levels; strong benefits for experienced hires.",
        "hiring_focus": "IT service management, workflow automation, enterprise AI.",
    },
    "cisco": {
        "priority_skills": [
            "networking", "python", "c", "c++", "linux", "distributed systems",
            "security", "rest api", "aws", "kubernetes",
        ],
        "culture_notes": (
            "Cisco combines hardware, networking OS, and cloud/security software. "
            "Strong fundamentals in networking protocols and OS internals are valued "
            "for infra roles. Security and cloud certifications help."
        ),
        "leveling_hint": "Associate vs individual contributor levels; diverse role types.",
        "hiring_focus": "Networking, security, collaboration tools (Webex), cloud security.",
    },
    "booking.com": {
        "priority_skills": [
            "python", "java", "perl", "sql", "system design",
            "machine learning", "aws", "kafka", "microservices", "a/b testing",
        ],
        "culture_notes": (
            "Booking.com is data-driven — A/B testing everything. Engineering "
            "culture is flat and ownership-heavy. Interviews mix coding with "
            "product/data reasoning questions."
        ),
        "leveling_hint": "Junior, Mid, Senior, Staff levels with clear growth paths.",
        "hiring_focus": "Travel marketplace, recommendation engines, payments, experimentation.",
    },
    "sap": {
        "priority_skills": [
            "java", "python", "abap", "sql", "hana", "rest api",
            "azure", "aws", "microservices", "agile",
        ],
        "culture_notes": (
            "SAP focuses on enterprise ERP and cloud transition. ABAP/HANA "
            "knowledge is a differentiator for platform roles. Strong emphasis "
            "on enterprise architecture and integration patterns."
        ),
        "leveling_hint": "Associate, Professional, Senior, Principal IC tracks.",
        "hiring_focus": "Enterprise software, S/4HANA, Business Technology Platform.",
    },
}


def get_profile(company_name: str):
    """Return the profile dict for a given company name (fuzzy match)."""
    if not company_name:
        return None
    key = company_name.strip().lower()
    # Exact key match
    if key in COMPANY_PROFILES:
        return {"name": key, **COMPANY_PROFILES[key]}
    # Substring match
    for name, profile in COMPANY_PROFILES.items():
        if name in key or key in name:
            return {"name": name, **profile}
    return None


def list_supported_companies():
    """Return display names of all supported companies."""
    return [name.title() for name in COMPANY_PROFILES.keys()]
