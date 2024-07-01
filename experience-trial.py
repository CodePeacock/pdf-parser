import re


def extract_experience_text(text):
    # Define the regex pattern
    experience_text_pattern = re.compile(
        r"(EXPERIENCE|Experience|Projects Undertaken:|PROJECTS UNDERTAKEN|Projects:|PROJECTS|PROJECTS:|Work Experience:|EMPLOYMENT HISTORY|Projects|Project Details:)\n([{L}\s\S]*?)(?=\n(?:SKILLS|Skills|Professional Skills|Personal Qualities:|PERSONAL QUALITIES:|Personal Qualities|PERSONAL QUALITIES|Education|EDUCATION|$))",
    )

    # Search for the first profile pattern in the text
    match = experience_text_pattern.search(text)

    # If a match is found, return the content after the first PROFILE paragraph
    return match[2].strip() if match else None


text = open(
    "resume-data\Harvi_3Yrs_Nodejs (2)\Harvi_3Yrs_Nodejs (2).txt", encoding="utf-8"
).read()
print(extract_experience_text(text))
