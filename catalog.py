"""
Focus OS — Predefined Habit & Domain Catalog
Includes 44 curated domains across 5 categories with extensible subtopic trees.
"""

CATALOG_CATEGORIES = [
    "Technology & Engineering",
    "Professional Development",
    "Personal Growth",
    "Health & Lifestyle",
    "Productivity & Focus"
]

DOMAIN_CATALOG = [
    # ----------------------------------------------------
    # Technology & Engineering (15 Domains)
    # ----------------------------------------------------
    {
        "id": "tech_dsa",
        "name": "DSA & Problem Solving",
        "category": "Technology & Engineering",
        "icon": "💻",
        "color": "#10b981",
        "daily_target": 8,
        "subtopics": [
            "Arrays", "Strings", "Hash Maps", "Linked Lists",
            "Stacks & Queues", "Trees", "Graphs", "Dynamic Programming",
            "Recursion", "Sorting & Searching", "Greedy Algorithms", "Binary Search"
        ]
    },
    {
        "id": "tech_ai",
        "name": "Artificial Intelligence",
        "category": "Technology & Engineering",
        "icon": "🤖",
        "color": "#06b6d4",
        "daily_target": 8,
        "subtopics": [
            "LLM Fundamentals", "RAG", "Agentic AI", "LangChain",
            "LangGraph", "LLM Evaluation", "LangSmith", "Langfuse",
            "Prompt Engineering", "Vector Databases", "Fine-Tuning", "Model Deployment"
        ]
    },
    {
        "id": "tech_ml",
        "name": "Machine Learning",
        "category": "Technology & Engineering",
        "icon": "🧠",
        "color": "#3b82f6",
        "daily_target": 8,
        "subtopics": [
            "Linear Models", "Decision Trees", "Ensemble Methods", "Neural Networks",
            "Feature Engineering", "Scikit-Learn", "PyTorch", "Model Evaluation",
            "Hyperparameter Tuning", "Computer Vision", "NLP Pipelines"
        ]
    },
    {
        "id": "tech_data_science",
        "name": "Data Science",
        "category": "Technology & Engineering",
        "icon": "📊",
        "color": "#0ea5e9",
        "daily_target": 6,
        "subtopics": [
            "Exploratory Data Analysis", "Pandas & NumPy", "Statistical Testing",
            "Data Cleaning", "Data Visualization", "Jupyter Workflows", "A/B Testing",
            "Predictive Modeling", "Big Data Basics"
        ]
    },
    {
        "id": "tech_data_analytics",
        "name": "Data Analytics",
        "category": "Technology & Engineering",
        "icon": "📈",
        "color": "#0284c7",
        "daily_target": 6,
        "subtopics": [
            "Advanced SQL", "Power BI", "Tableau", "Excel & Dashboards",
            "Business Metrics", "Cohort Analysis", "ETL Pipelines", "Data Storytelling"
        ]
    },
    {
        "id": "tech_backend",
        "name": "Backend Development",
        "category": "Technology & Engineering",
        "icon": "⚙️",
        "color": "#6366f1",
        "daily_target": 8,
        "subtopics": [
            "REST APIs", "FastAPI / Python", "Node.js / Express", "Authentication & JWT",
            "Database Design", "Redis Caching", "Message Queues", "Microservices",
            "API Security", "GraphQL", "ORM & Query Tuning"
        ]
    },
    {
        "id": "tech_frontend",
        "name": "Frontend Development",
        "category": "Technology & Engineering",
        "icon": "🎨",
        "color": "#8b5cf6",
        "daily_target": 8,
        "subtopics": [
            "HTML & Semantic Web", "Modern CSS & Flex/Grid", "JavaScript ES6+",
            "TypeScript", "React", "Next.js", "Tailwind CSS",
            "State Management", "Performance Optimization", "Web Accessibility (a11y)"
        ]
    },
    {
        "id": "tech_fullstack",
        "name": "Full Stack Development",
        "category": "Technology & Engineering",
        "icon": "⚡",
        "color": "#a855f7",
        "daily_target": 8,
        "subtopics": [
            "End-to-End Architecture", "Database to UI", "API Contracts",
            "Serverless Functions", "State Synchronization", "Full Stack Testing",
            "WebSockets", "Monorepo Management"
        ]
    },
    {
        "id": "tech_devops",
        "name": "DevOps & Cloud",
        "category": "Technology & Engineering",
        "icon": "☁️",
        "color": "#9333ea",
        "daily_target": 8,
        "subtopics": [
            "Docker & Containers", "Kubernetes", "AWS Cloud Services", "Azure Cloud",
            "CI/CD Pipelines", "GitHub Actions", "Terraform & IaC", "Monitoring & Prometheus",
            "Linux Server Administration", "Cloud Networking"
        ]
    },
    {
        "id": "tech_cyber",
        "name": "Cybersecurity",
        "category": "Technology & Engineering",
        "icon": "🛡️",
        "color": "#f59e0b",
        "daily_target": 6,
        "subtopics": [
            "Linux Hardening", "Network Security", "OverTheWire Labs",
            "OWASP Top 10", "Penetration Testing", "Cryptography Basics",
            "SIEM & Threat Detection", "Web Vulnerability Scanning", "Identity Management"
        ]
    },
    {
        "id": "tech_system_design",
        "name": "System Design",
        "category": "Technology & Engineering",
        "icon": "🏛️",
        "color": "#d97706",
        "daily_target": 6,
        "subtopics": [
            "Horizontal Scaling", "Load Balancing", "Database Sharding & Replication",
            "Caching Strategies", "CAP Theorem", "Rate Limiting", "Message Brokers",
            "CDN & Edge Networks", "High Availability Architectures"
        ]
    },
    {
        "id": "tech_databases",
        "name": "Database Engineering",
        "category": "Technology & Engineering",
        "icon": "🗄️",
        "color": "#b45309",
        "daily_target": 6,
        "subtopics": [
            "PostgreSQL Internals", "Query Optimization & EXPLAIN", "Indexing Techniques",
            "ACID & Transactions", "Connection Pooling", "MySQL", "MongoDB / NoSQL",
            "Vector Embeddings Storage"
        ]
    },
    {
        "id": "tech_mobile",
        "name": "Mobile Development",
        "category": "Technology & Engineering",
        "icon": "📱",
        "color": "#ec4899",
        "daily_target": 6,
        "subtopics": [
            "React Native", "Flutter", "iOS / Swift", "Android / Kotlin",
            "Mobile UI Patterns", "Offline Storage", "Push Notifications", "App Store Deployment"
        ]
    },
    {
        "id": "tech_software_eng",
        "name": "Software Engineering",
        "category": "Technology & Engineering",
        "icon": "🛠️",
        "color": "#14b8a6",
        "daily_target": 8,
        "subtopics": [
            "Clean Code Practices", "Design Patterns", "Unit & Integration Testing",
            "Git & Version Control", "Code Review Excellence", "Refactoring", "Documentation"
        ]
    },
    {
        "id": "tech_opensource",
        "name": "Open Source Development",
        "category": "Technology & Engineering",
        "icon": "🌐",
        "color": "#0d9488",
        "daily_target": 4,
        "subtopics": [
            "Issue Triage", "Pull Request Contributions", "OSS Project Maintenance",
            "Bug Fixing", "Community Engagement", "Documentation Writing"
        ]
    },

    # ----------------------------------------------------
    # Professional Development (8 Domains)
    # ----------------------------------------------------
    {
        "id": "prof_career",
        "name": "Career Development",
        "category": "Professional Development",
        "icon": "🚀",
        "color": "#3b82f6",
        "daily_target": 4,
        "subtopics": [
            "Resume Refinement", "Portfolio Projects", "Interview Preparation",
            "Networking", "LinkedIn Optimization", "Skill Gap Analysis", "Mentorship"
        ]
    },
    {
        "id": "prof_communication",
        "name": "Communication Skills",
        "category": "Professional Development",
        "icon": "🗣️",
        "color": "#06b6d4",
        "daily_target": 4,
        "subtopics": [
            "Technical Writing", "Public Speaking", "Active Listening",
            "Executive Presentations", "Storytelling", "Cross-functional Collaboration"
        ]
    },
    {
        "id": "prof_leadership",
        "name": "Leadership",
        "category": "Professional Development",
        "icon": "👑",
        "color": "#f59e0b",
        "daily_target": 4,
        "subtopics": [
            "Team Motivation", "Delegation", "Conflict Resolution",
            "Strategic Thinking", "Decisiveness", "1-on-1 Coaching", "Vision Setting"
        ]
    },
    {
        "id": "prof_entrepreneurship",
        "name": "Entrepreneurship",
        "category": "Professional Development",
        "icon": "💡",
        "color": "#eab308",
        "daily_target": 6,
        "subtopics": [
            "Idea Validation", "Customer Discovery", "MVP Building",
            "Product-Market Fit", "Pricing Strategy", "Fundraising Basics", "Legal Setup"
        ]
    },
    {
        "id": "prof_biz_dev",
        "name": "Business Development",
        "category": "Professional Development",
        "icon": "🤝",
        "color": "#10b981",
        "daily_target": 4,
        "subtopics": [
            "Partnership Strategy", "Market Analysis", "Pipeline Management",
            "Deal Negotiation", "Relationship Building", "Contract Review"
        ]
    },
    {
        "id": "prof_marketing",
        "name": "Sales & Marketing",
        "category": "Professional Development",
        "icon": "📣",
        "color": "#ef4444",
        "daily_target": 4,
        "subtopics": [
            "Content Marketing", "Cold Outreach", "SEO Fundamentals",
            "Social Media Strategy", "Email Campaigns", "Conversion Optimization"
        ]
    },
    {
        "id": "prof_branding",
        "name": "Personal Branding",
        "category": "Professional Development",
        "icon": "✨",
        "color": "#ec4899",
        "daily_target": 2,
        "subtopics": [
            "Thought Leadership", "Writing Online", "Twitter/X Sprints",
            "Substack / Newsletter", "Podcast Appearances", "Conference Speaking"
        ]
    },
    {
        "id": "prof_finance",
        "name": "Financial Literacy",
        "category": "Professional Development",
        "icon": "💰",
        "color": "#84cc16",
        "daily_target": 2,
        "subtopics": [
            "Budgeting & Cash Flow", "Investing Strategies", "Tax Planning",
            "Emergency Funds", "Real Estate Basics", "Retirement Modeling"
        ]
    },

    # ----------------------------------------------------
    # Personal Growth (7 Domains)
    # ----------------------------------------------------
    {
        "id": "grow_reading",
        "name": "Reading",
        "category": "Personal Growth",
        "icon": "📚",
        "color": "#8b5cf6",
        "daily_target": 2,
        "subtopics": [
            "Technical Books", "Non-fiction", "Philosophy",
            "Biographies", "Paper Summaries", "Audiobooks", "Book Notes"
        ]
    },
    {
        "id": "grow_writing",
        "name": "Writing",
        "category": "Personal Growth",
        "icon": "✍️",
        "color": "#a855f7",
        "daily_target": 2,
        "subtopics": [
            "Essays", "Daily Notes", "Blog Posts",
            "Documentation", "Creative Writing", "Clear Thinking Exercises"
        ]
    },
    {
        "id": "grow_meditation",
        "name": "Meditation",
        "category": "Personal Growth",
        "icon": "🧘",
        "color": "#10b981",
        "daily_target": 1,
        "subtopics": [
            "Breath Awareness", "Mindfulness", "Box Breathing",
            "Body Scan", "Loving Kindness", "Vipassana", "Morning Zen"
        ]
    },
    {
        "id": "grow_journaling",
        "name": "Journaling",
        "category": "Personal Growth",
        "icon": "📖",
        "color": "#06b6d4",
        "daily_target": 1,
        "subtopics": [
            "Morning Pages", "Evening Reflection", "Gratitude Prompts",
            "Decision Logs", "Goal Check-ins", "Emotional Check-ins"
        ]
    },
    {
        "id": "grow_learning",
        "name": "Learning & Research",
        "category": "Personal Growth",
        "icon": "🔬",
        "color": "#3b82f6",
        "daily_target": 4,
        "subtopics": [
            "Scientific Papers", "Online Courses", "Speed Reading",
            "Feynman Technique", "Anki Spaced Repetition", "Concept Mapping"
        ]
    },
    {
        "id": "grow_languages",
        "name": "Language Learning",
        "category": "Personal Growth",
        "icon": "🗣️",
        "color": "#f59e0b",
        "daily_target": 2,
        "subtopics": [
            "Vocabulary Drill", "Grammar Practice", "Listening Comprehension",
            "Speaking Drills", "Reading Articles", "Language Exchange"
        ]
    },
    {
        "id": "grow_creativity",
        "name": "Creativity",
        "category": "Personal Growth",
        "icon": "🎨",
        "color": "#f43f5e",
        "daily_target": 2,
        "subtopics": [
            "Brainstorming Sprints", "Visual Art", "Music & Instruments",
            "Lateral Thinking", "Sketching Ideas", "Creative Experiments"
        ]
    },

    # ----------------------------------------------------
    # Health & Lifestyle (8 Domains)
    # ----------------------------------------------------
    {
        "id": "health_workout",
        "name": "Morning Workout",
        "category": "Health & Lifestyle",
        "icon": "🏋️",
        "color": "#3b82f6",
        "daily_target": 2,
        "subtopics": [
            "Calisthenics", "Core Routine", "High Intensity Intervals",
            "Dynamic Stretching", "Morning Cardio", "Kettlebell Complexes"
        ]
    },
    {
        "id": "health_strength",
        "name": "Strength Training",
        "category": "Health & Lifestyle",
        "icon": "💪",
        "color": "#2563eb",
        "daily_target": 2,
        "subtopics": [
            "Compound Lifts", "Squat / Bench / Deadlift", "Hypertrophy",
            "Progressive Overload", "Rest & Recovery", "Warmup Sets"
        ]
    },
    {
        "id": "health_running",
        "name": "Running & Cardio",
        "category": "Health & Lifestyle",
        "icon": "🏃",
        "color": "#0284c7",
        "daily_target": 2,
        "subtopics": [
            "5K Pace Training", "Long Slow Distance", "Sprint Intervals",
            "Zone 2 Cardio", "Cadence Training", "Trail Running"
        ]
    },
    {
        "id": "health_yoga",
        "name": "Yoga & Mobility",
        "category": "Health & Lifestyle",
        "icon": "🧘",
        "color": "#10b981",
        "daily_target": 1,
        "subtopics": [
            "Vinyasa Flow", "Hip Mobility", "Spine Decompression",
            "Hamstring Flexibility", "Balance Poses", "Yin Yoga"
        ]
    },
    {
        "id": "health_hydration",
        "name": "Hydration",
        "category": "Health & Lifestyle",
        "icon": "💧",
        "color": "#06b6d4",
        "daily_target": 1,
        "subtopics": [
            "2.5L Water Intake", "Morning Lemon Water", "Electrolyte Balancing",
            "Post-workout Hydration", "Herbal Tea"
        ]
    },
    {
        "id": "health_nutrition",
        "name": "Nutrition",
        "category": "Health & Lifestyle",
        "icon": "🥗",
        "color": "#84cc16",
        "daily_target": 1,
        "subtopics": [
            "Whole Foods", "High Protein", "Limit Refined Sugar",
            "Meal Prepping", "Intermittent Fasting", "Micronutrient Tracking"
        ]
    },
    {
        "id": "health_sleep",
        "name": "Sleep Routine",
        "category": "Health & Lifestyle",
        "icon": "🌙",
        "color": "#ec4899",
        "daily_target": 8,
        "subtopics": [
            "Sleep by 11:00 PM", "No Screens 1h Before Bed", "Cool Room Temp",
            "8 Hours Duration", "Consistent Wake Time", "Wind-down Routine"
        ]
    },
    {
        "id": "health_walking",
        "name": "Walking",
        "category": "Health & Lifestyle",
        "icon": "👟",
        "color": "#14b8a6",
        "daily_target": 2,
        "subtopics": [
            "8,000 Steps Daily", "Post-meal Walks", "Nature Strolls",
            "Walking Meetings", "Evening Cool-down Walk"
        ]
    },

    # ----------------------------------------------------
    # Productivity & Focus (6 Domains)
    # ----------------------------------------------------
    {
        "id": "prod_deep_work",
        "name": "Deep Work",
        "category": "Productivity & Focus",
        "icon": "🎯",
        "color": "#f59e0b",
        "daily_target": 4,
        "subtopics": [
            "2-hr Focus Blocks", "Zero Distractions", "Pomodoro Cycles",
            "Flow State Triggers", "Deep Problem Solving", "Single-tasking"
        ]
    },
    {
        "id": "prod_time_mgmt",
        "name": "Time Management",
        "category": "Productivity & Focus",
        "icon": "⏱️",
        "color": "#d97706",
        "daily_target": 2,
        "subtopics": [
            "Time Blocking", "Eisenhower Matrix", "Priority MITs",
            "Calendar Audits", "Saying No", "Batch Processing"
        ]
    },
    {
        "id": "prod_planning",
        "name": "Planning & Reflection",
        "category": "Productivity & Focus",
        "icon": "📋",
        "color": "#6366f1",
        "daily_target": 1,
        "subtopics": [
            "Daily Standup", "Weekly Review", "Monthly Retrospective",
            "OKR Tracking", "Backlog Grooming", "Next Day Preparation"
        ]
    },
    {
        "id": "prod_digital_disc",
        "name": "Digital Discipline",
        "category": "Productivity & Focus",
        "icon": "📵",
        "color": "#ef4444",
        "daily_target": 2,
        "subtopics": [
            "Screen Time Limits", "No Social Feeds", "Notification Silence",
            "App Blockers", "Inbox Zero", "Clean Desktop Workspace"
        ]
    },
    {
        "id": "prod_consistency",
        "name": "Consistency Building",
        "category": "Productivity & Focus",
        "icon": "⚡",
        "color": "#10b981",
        "daily_target": 2,
        "subtopics": [
            "Never Miss Twice", "Habit Stacking", "Micro-habits",
            "Friction Reduction", "Identity Reinforcement", "Accountability Tracking"
        ]
    },
    {
        "id": "prod_projects",
        "name": "Personal Projects",
        "category": "Productivity & Focus",
        "icon": "🚀",
        "color": "#84cc16",
        "daily_target": 4,
        "subtopics": [
            "SaaS Building", "Research & Experiments", "Content Production",
            "Open Source Tooling", "Automation Scripts", "Portfolio Updates"
        ]
    }
]

def get_catalog_categories():
    return CATALOG_CATEGORIES

def get_domain_catalog():
    return DOMAIN_CATALOG

def find_domain_by_name_or_id(query: str):
    q = query.strip().lower()
    for item in DOMAIN_CATALOG:
        if item["id"].lower() == q or item["name"].lower() == q:
            return item
    return None

