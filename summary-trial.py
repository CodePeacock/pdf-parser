import re


def extract_profile(text_content):
    # Define the regex pattern
    profile_pattern = re.compile(
        r"(?i)\b(?:Profile|Summary|Objective|Career Objective|Professional Summary|About Me)\b(?:.*?\n\n(.+?)(?=\n\n|$))?",
        re.DOTALL,
    )

    # Search for the profile pattern in the text
    matches = profile_pattern.findall(text_content)

    # If matches are found, return a list of extracted profiles, otherwise return None
    return [match.strip() for match in matches if match] if matches else None


# Example usage:
pdf_text = """
MAYUR SINALKAR

Python Developer | AI-ML Developer

+919967342073 + mayursinalkar404@gmail.com https://www.linkedin.com/in/mayur-sinalkar Ghansoli, Navi Mumbai

SUMMARY

Dedicated fresher driven by a strong desire to channel my skills and unwavering enthusiasm for innovation towards the development of sophisticated Al systems aimed at tackling tangible real-world problems while elevating user interactions. Actively pursuing opportunities within a progressive organization to contribute meaningfully to societal advancement.

EDUCATION

Master of Science in Information Technology

SIES(Nerul) College of Arts, Science and Commerce (Autonomous)

Nerul, Navi Mumbai 07/2021 - 07/2023

Bachelor of Science in Information Technology

Bhavna Trust Junior & Degree College of Commerce & Science

Deonar, Mumbai 07/2018 - 05/2021

SKILLS

Python: Machine Learning, NLP, NLU, Al, Flask, FastAPI

Web Programming: HTML, CSS, JavaScript

Virtualization: VMWare, VirtualBox

PROJECTS

TrelloTalk: The Voice-Powered Taskmaster

12/2022 - 07/2023 SIES(Nerul)

TrelloTalk streamlines Trello management through seamless text and voice interactions, facilitated by a ReactUS-based UI. The Whisper ASR ensures accurate voice-to-text conversion, and FastAPI efficiently communicates with the Trello API. Further enhancing the user experience, Rasa NLU interprets intent, ultimately optimizing task management and boosting overall productivity.

Student Attendance Management

05/2021 - 07/2021 Bhavna Trust(Deonar)

The Student Attendance Management system simplifies the attendance tracking process, enabling teachers to effortlessly add subjects, batches, and students. This project was meticulously developed using Flutter and Firebase technologies.

COURSES & CERTIFICATES

Python Advance Level Il MUQuestionPapers

Applied Data Science with Python Simplilearn

STRENGTHS

Innovative Al Development

Dedication to Learning

Enthusiastic Problem Solver

Passionate about creating sophisticated Al systems to address real-world issues.

Driven by a strong desire to continuously acquire new skills and knowledge.

Eager to contribute towards societal advancement through innovative solutions.

Effective Communication

Adept at facilitating seamless interactions and collaborations within project teams.

...
"""

# Extract the profiles
profiles = extract_profile(pdf_text)

# Print the result
if profiles:
    for i, profile in enumerate(profiles, start=1):
        with open(f"profile_{i}.txt", "w") as f:
            f.write(profile)
else:
    print("No profile sections detected.")
