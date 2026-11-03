"""Transparent, rule-based resume/job-description analysis (no AI or database)."""
import re
from collections import Counter

SKILL_GROUPS = {
    "Programming": ["python", "java", "javascript", "typescript", "c++", "c#", "r", "php", "go", "html", "css", "sql", "bash"],
    "Frameworks": ["flask", "django", "fastapi", "react", "angular", "vue", "node.js", "spring boot", "express", "rest api"],
    "Data & AI": ["excel", "power bi", "tableau", "pandas", "numpy", "matplotlib", "machine learning", "statistics", "data analysis", "data visualization", "scikit-learn", "tensorflow", "pytorch"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "ci/cd", "linux", "terraform"],
    "Cybersecurity": ["networking", "wireshark", "siem", "incident response", "security monitoring", "risk assessment", "penetration testing", "firewalls", "splunk", "nmap"],
    "Business & Collaboration": ["communication", "leadership", "project management", "agile", "scrum", "problem solving", "customer service", "stakeholder management"],
}

ALIASES = {
    "node.js": ["nodejs", "node js"], "power bi": ["powerbi"], "rest api": ["restful api", "rest apis"],
    "ci/cd": ["continuous integration", "continuous delivery"], "scikit-learn": ["sklearn"],
    "javascript": ["java script"], "machine learning": ["ml"], "aws": ["amazon web services"],
    "gcp": ["google cloud platform"], "siem": ["security information and event management"],
    "html": ["html5"], "css": ["css3"], "c#": ["c sharp"], "c++": ["cpp"],
}


def contains_skill(text, skill):
    """Match whole skill terms rather than substrings (R != 'are', Go != 'good')."""
    for term in [skill, *ALIASES.get(skill, [])]:
        pattern = r"(?<![\w])" + re.escape(term) + r"(?![\w])"
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def list_skills(text):
    return {category: [s for s in skills if contains_skill(text, s)] for category, skills in SKILL_GROUPS.items()}


def analyze(resume, job, role="Target Role"):
    detected = list_skills(resume)
    required = list_skills(job)
    matched = {cat: [s for s in req if s in detected[cat]] for cat, req in required.items()}
    missing = {cat: [s for s in req if s not in detected[cat]] for cat, req in required.items()}
    num_req = sum(map(len, required.values()))
    num_match = sum(map(len, matched.values()))
    percentage = round(100 * num_match / num_req) if num_req else None
    category_chart = []
    for cat in SKILL_GROUPS:
        if required[cat]:
            category_chart.append({"category": cat, "matched": len(matched[cat]), "missing": len(missing[cat])})
    missing_flat = [s for v in missing.values() for s in v]
    matched_flat = [s for v in matched.values() for s in v]
    resume_only = [s for cat, skills in detected.items() for s in skills if s not in required[cat]]
    suggestions = []
    if not num_req:
        suggestions.append("No recognized skills were found in the job description. Try a longer description with explicit skill requirements. No match percentage is calculated.")
    elif missing_flat:
        suggestions.append("Prioritize these skills mentioned in the job description: " + ", ".join(missing_flat[:5]) + ".")
        suggestions.append("If you genuinely have these skills, describe them with concrete evidence in your resume; otherwise consider developing them.")
    else:
        suggestions.append("All recognized job-description skills appear in the resume. Review the depth of your experience, projects, and achievements too.")
    if len(resume.split()) < 100:
        suggestions.append("The resume contains fewer than 100 extracted words. Consider adding specific project outcomes, work evidence, and achievements if relevant.")
    suggestions.append("Tailor your resume to the role using truthful, measurable examples, rather than repeating keywords.")
    questions = [f"Tell me about a project or task where you used {s}." for s in (missing_flat + matched_flat)[:4]]
    return {
        "role": role.strip()[:90] or "Target Role", "score": percentage,
        "required_count": num_req, "matched_count": num_match,
        "matched": matched_flat, "missing": missing_flat, "other_skills": resume_only,
        "categories": category_chart, "suggestions": suggestions, "questions": questions,
        "resume_word_count": len(resume.split()), "job_word_count": len(job.split()),
    }
