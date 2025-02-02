import re

def extract_resume_data(text):
    name = re.search(r"([A-Z][a-z]+\s[A-Z][a-z]+)", text)  # Basic regex for name
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    education = re.findall(
        r"(Bachelor['’]?\s?(of\s[A-Za-z]+|\w+)\s?[A-Za-z]+|Master['’]?\s?(of\s[A-Za-z]+|\w+)\s?[A-Za-z]+|PhD\s?[A-Za-z]*|Associate['’]?\s?[A-Za-z]+|[A-Za-z]+\sDegree|University[\sA-Za-z]+|College[\sA-Za-z]+)[^\n]*",
        text, re.IGNORECASE)

    education = [' '.join(filter(None, edu)).strip() for edu in education]

    skills = ["Python", "Django", "Machine Learning", "AI", "JavaScript", "React", "SQL"]
    found_skills = [skill for skill in skills if skill.lower() in text.lower()]

    applied_for = re.search(r"Applied\s*for[:\s]*(.*)", text, re.IGNORECASE)
    applied_for = applied_for.group(1).strip() if applied_for else "Not Found"

    experience = re.search(r"Experience[:\s]*(\d+[\s\w]*)", text, re.IGNORECASE)
    experience = experience.group(1).strip() if experience else "Not Found"

    current_ctc = re.search(r"Current\s*CTC[:\s]*([\d,]+(?:\s?[kK]|\s?[lL]?\s?pa)?)", text, re.IGNORECASE)
    current_ctc = current_ctc.group(1).strip() if current_ctc else "Not Found"

    expected_ctc = re.search(r"Expected\s*CTC[:\s]*([\d,]+(?:\s?[kK]|\s?[lL]?\s?pa)?)", text, re.IGNORECASE)
    expected_ctc = expected_ctc.group(1).strip() if expected_ctc else "Not Found"

    return {
        "name": name.group() if name else "Unknown",
        "email": email.group() if email else "Not Found",
        "phone": phone.group() if phone else "Not Found",
        "skills": found_skills,
        "education": education if education else ["Not Found"],
        "applied_for": applied_for,
        "experience": experience,
        "current_ctc": current_ctc,
        "expected_ctc": expected_ctc
    }