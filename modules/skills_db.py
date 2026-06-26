"""
skills_db.py
Comprehensive, categorized skill database for production-grade matching.
Includes aliases, synonyms, and multi-word skills across all major tech domains.
"""

# ── Programming Languages ──────────────────────────────────────────────────
LANGUAGES = [
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go",
    "golang", "rust", "kotlin", "swift", "scala", "ruby", "php", "r",
    "matlab", "dart", "perl", "haskell", "elixir", "clojure", "groovy",
    "objective-c", "assembly", "cobol", "fortran", "lua", "julia",
]

# ── Frontend ───────────────────────────────────────────────────────────────
FRONTEND = [
    "html", "css", "react", "react.js", "next.js", "vue", "vue.js", "angular",
    "svelte", "redux", "zustand", "mobx", "tailwind", "tailwind css",
    "bootstrap", "material ui", "chakra ui", "shadcn", "ant design",
    "webpack", "vite", "babel", "sass", "scss", "less", "jquery",
    "react native", "flutter", "electron", "streamlit", "gradio",
    "web components", "pwa", "webassembly", "wasm", "d3.js", "three.js",
]

# ── Backend & Frameworks ───────────────────────────────────────────────────
BACKEND = [
    "node.js", "express", "express.js", "fastapi", "django", "flask",
    "spring", "spring boot", "spring mvc", "asp.net", ".net", ".net core",
    "rails", "ruby on rails", "laravel", "nestjs", "hapi", "koa",
    "graphql", "rest api", "restful api", "rest", "grpc", "websocket",
    "oauth", "jwt", "api design", "microservices", "serverless",
    "event driven", "message queue", "celery", "fastify",
]

# ── Databases ──────────────────────────────────────────────────────────────
DATABASES = [
    "mysql", "postgresql", "postgres", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "firebase", "firestore", "sqlite", "oracle",
    "oracle db", "sql server", "mssql", "mariadb", "cockroachdb",
    "neo4j", "influxdb", "clickhouse", "snowflake", "bigquery",
    "vector database", "pinecone", "weaviate", "chroma", "qdrant",
    "supabase", "planetscale", "neon",
]

# ── Cloud & DevOps ─────────────────────────────────────────────────────────
CLOUD_DEVOPS = [
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "terraform", "ansible", "helm", "ci/cd", "jenkins", "github actions",
    "gitlab ci", "circleci", "travis ci", "argocd", "nginx", "apache",
    "linux", "bash", "shell scripting", "powershell", "vagrant",
    "serverless framework", "aws lambda", "aws ec2", "aws s3", "aws rds",
    "aws ecs", "aws eks", "aws cloudformation", "aws iam",
    "azure devops", "azure functions", "azure aks",
    "gke", "cloud run", "cloud functions",
    "prometheus", "grafana", "datadog", "splunk", "elk stack",
    "istio", "service mesh", "load balancing", "cdn",
]

# ── Version Control & Collaboration ───────────────────────────────────────
VCS = [
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "notion",
    "linear", "trello", "asana", "slack", "figma",
]

# ── AI / ML / Data Science ─────────────────────────────────────────────────
AI_ML = [
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "reinforcement learning", "supervised learning",
    "unsupervised learning", "neural networks", "transformers",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "xgboost", "lightgbm", "catboost", "huggingface", "langchain",
    "llm", "large language models", "generative ai", "gen ai",
    "prompt engineering", "rag", "retrieval augmented generation",
    "fine tuning", "embeddings", "semantic search",
    "spacy", "nltk", "gensim", "opencv", "pillow",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly", "bokeh",
    "data analysis", "data science", "data engineering", "data pipeline",
    "feature engineering", "model deployment", "mlops", "mlflow",
    "airflow", "spark", "hadoop", "kafka", "flink",
    "tableau", "power bi", "looker", "dbt", "etl", "elt",
    "statistics", "linear algebra", "calculus",
    "a/b testing", "hypothesis testing", "regression", "classification",
]

# ── Software Engineering Practices ─────────────────────────────────────────
SWE = [
    "system design", "distributed systems", "scalability", "high availability",
    "data structures", "algorithms", "oop", "object oriented programming",
    "functional programming", "design patterns", "solid principles",
    "tdd", "test driven development", "bdd", "unit testing", "integration testing",
    "e2e testing", "selenium", "playwright", "cypress", "pytest", "junit",
    "jest", "mocha", "qa automation", "code review", "pair programming",
    "agile", "scrum", "kanban", "sprint planning", "retrospective",
    "rest", "soap", "api gateway", "caching", "message broker",
    "concurrency", "multithreading", "async programming",
    "security", "oauth2", "saml", "zero trust", "encryption",
    "web scraping", "beautifulsoup", "scrapy", "puppeteer",
]

# ── Mobile ─────────────────────────────────────────────────────────────────
MOBILE = [
    "android", "ios", "android studio", "xcode", "jetpack compose",
    "swiftui", "kotlin multiplatform", "capacitor", "ionic",
]

# ── Soft Skills & Leadership ───────────────────────────────────────────────
SOFT_SKILLS = [
    "leadership", "ownership", "communication", "stakeholder management",
    "problem solving", "critical thinking", "collaboration", "mentoring",
    "cross functional", "project management", "product sense", "customer focus",
    "attention to detail", "time management", "adaptability",
]

# ── Combine all ───────────────────────────────────────────────────────────
SKILLS = (
    LANGUAGES + FRONTEND + BACKEND + DATABASES + CLOUD_DEVOPS +
    VCS + AI_ML + SWE + MOBILE + SOFT_SKILLS
)

# Deduplicate while preserving order
_seen = set()
SKILLS = [s for s in SKILLS if not (s in _seen or _seen.add(s))]

SKILLS_LOWER_SET = set(s.lower() for s in SKILLS)

# ── Synonym / alias map ────────────────────────────────────────────────────
# Maps alias → canonical skill name (all lowercase)
SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "golang": "go",
    "k8s": "kubernetes",
    "ml": "machine learning",
    "dl": "deep learning",
    "cv": "computer vision",
    "tf": "tensorflow",
    "sk-learn": "scikit-learn",
    "hf": "huggingface",
    "llms": "llm",
    "genai": "generative ai",
    "rag": "retrieval augmented generation",
    "node": "node.js",
    "react.js": "react",
    "vue.js": "vue",
    "next": "next.js",
    "pg": "postgresql",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "elastic": "elasticsearch",
    "aws lambda": "aws",
    "aws ec2": "aws",
    "gcp": "google cloud",
    "azure devops": "azure",
    "spring boot": "spring",
    "dsa": "data structures",
    "ds": "data structures",
    "oops": "oop",
    "ci cd": "ci/cd",
    "restful": "rest api",
    "rest apis": "rest api",
    "graphql api": "graphql",
    "shell": "bash",
    "cmd": "bash",
    "git hub": "github",
    "tailwindcss": "tailwind",
    "tailwind css": "tailwind",
    "materialui": "material ui",
    "chakrui": "chakra ui",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "pytorch lightning": "pytorch",
    "hugging face": "huggingface",
    "lang chain": "langchain",
    "large language model": "llm",
    "generative ai": "gen ai",
    "retrieval augmented generation": "rag",
    "natural language processing": "nlp",
    "object oriented": "oop",
    "object oriented programming": "oop",
    "test driven": "tdd",
    "agile methodology": "agile",
    "scrum methodology": "scrum",
}

# ── Category labels for display ────────────────────────────────────────────
SKILL_CATEGORIES = {
    "Languages": LANGUAGES,
    "Frontend": FRONTEND,
    "Backend": BACKEND,
    "Databases": DATABASES,
    "Cloud & DevOps": CLOUD_DEVOPS,
    "AI / ML": AI_ML,
    "Software Engineering": SWE,
    "Mobile": MOBILE,
    "Soft Skills": SOFT_SKILLS,
}
