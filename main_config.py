"""
All regex patterns used in the modules are defined here.

This module is used by the main.py module to extract data from the text files.

List of Functions:
- extract_phone(text_content: str) -> str: Extracts a phone number from the given text content.
- extract_email(text_content: str) -> str | None: Extracts the first email address found in the given text content.
- extract_experience_duration(text: str) -> tuple[float, str]: Extracts the numeric value and duration string from the given text using a regular expression pattern.
- extract_experience_text(text: str) -> str | Any | None: Extracts the experience text from the given input text.
- extract_summary_text(text_content: str) -> str | Any | None: Extracts the summary from the given text content.

List of Regex Patterns:
- PINCODE_PATTERN: Regex pattern for pincode.
- EMAIL_PATTERN: Regex pattern for email address.
- PHONE_PATTERN: Regex pattern for phone number.
- LINK_PATTERN: Regex pattern for link.
- EXPERIENCE_DURATION_PATTERN: Regex pattern for experience duration.
- NAME_PATTERN: Regex pattern for name.
- EXPERIENCE_TEXT_PATTERN: Regex pattern for experience text.
- SUMMARY_PATTERN: Regex pattern for summary.

"""


import codecs
import re
from typing import Any, Literal

# All Regex Patterns
PINCODE_PATTERN = re.compile(r"\b\d{6}\b")

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

PHONE_PATTERN = re.compile(r"(\+?\d{0,3}[-\s]?\d{10})")

LINK_PATTERN = re.compile(r".*\.com.*\n?")

EXPERIENCE_DURATION_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:[yY]ears|[yY]ear|[mM]onths?)"
)

NAME_PATTERN = re.compile(
    r"^(?:.*?(?:Name:\s*)?(?:Mrs\.|Mr\.|Miss|Ms\.)?\s*([A-Za-z]+)\s*([A-Za-z]+(?: [A-Za-z]+)*))\n?",
)

EXPERIENCE_TEXT_PATTERN = re.compile(
    r"(EXPERIENCE|Experience|Projects Undertaken:|PROJECTS UNDERTAKEN|Projects:|PROJECTS|PROJECTS:|Work Experience:|EMPLOYMENT HISTORY|Projects|Project Details:|WORK EXPERIENCE :|Projects :|EXPERIENCE:|Project|Employment History|PR O F E S SI O NA L   E X P E R I E N C E|Work experience|PROFESSIONAL EXPERIENCE .|P R O J E C T S|JOBS|W O R K E X P E R I E N C E|Work History|PROJECT)\n([{L}\s\S]*?)(?=\n(?:SKILLS|Skills|Professional Skills|Personal Qualities:|PERSONAL QUALITIES:|Personal Qualities|PERSONAL QUALITIES|Education|EDUCATION|EXTRACURRICULAR ACTIVITIES|Languages|Certification|CERTIFICATE|Additional Information:|ACHIEVEMENTS|E D U C A TI O N|Interests|TECHNICAL SKILLS|SKILLS:|TRAINING|P R O J E C T S|S K I L L S|STRENGTHS|$))",
)

SUMMARY_PATTERN = re.compile(
    r"(\bSummary|ABOUT|PROFILE|SUMMARY|INTRODUCTION|HEADLINE|PROFESSIONAL SUMMARY|About Me|PROFESSIONAL SUMMARY:|Synopsis|Proﬁle Summary:|Profile Summary:|My Projects|Summary|SUMMARY|Summary:|CAREER OBJECTIVE :|Objectives :|Projects:|Objectives|Objective|Profile|SUMMARY OF EXPERIENCE|OBJECTIVE|CAREER SUMMARY:|ABOUT ME|Objective:|P R O F E S S I O N A L   S U M M A R Y|CAREER OBJECTIVE:|P R O F I L E|Profile Summary & Skills|CAREER OBJECTIVE)\n?([\s\S]*?)(?=\n(?:CAREER OBJECTIVE|OBJECTIVE|GOAL|Education|EXPERIENCE SUMMARY|Current Company Details|Projects Undertaken|Experience|Skills|Contact|Technical Skills|Technical Expertise:|Professional Qualification|EMPLOYMENT HISTORY|Completed|EDUCATION|Projects|SKILLS|Languages|Current|PROFESSIONAL|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|T E C H N I C A L   S K I L L S|C O N T A C T M E|Work Experience|E D U C A T I O N|Professional Experience|Skills & Abilities|QUALIFICATION DETAILS|$)\b)",
    flags=re.DOTALL,
)

URL_TO_FETCH_SKILL = "https://api.npoint.io/81a5d37fea0d63fea458"
URL_TO_FETCH_DESIGNATION = "https://api.npoint.io/5bb9a9836361d1fc9396"


def extract_email(text_content: str) -> str | None:
    """
    Extracts an email address from the given text content.

    Args:
        text_content (str): The text content to search for an email address.

    Returns:
        str | None: The extracted email address, or None if no match is found.
    """
    match = re.search(pattern=EMAIL_PATTERN, string=text_content)
    return match.group() if match else None


def extract_phone(text_content: str) -> str | Any | None:
    """
    Extracts a phone number from the given text content.

    Args:
        text_content (str): The text content from which to extract the phone number.

    Returns:
        str | Any | None: The extracted phone number, or None if no phone number is found.
    """
    pincode = re.search(PINCODE_PATTERN, text_content)
    try:
        if pincode:
            text_content = text_content.replace(pincode[0], "")
        else:
            text_content = text_content
    except Exception as e:
        print("Exception", e)

    if match := re.search(PHONE_PATTERN, text_content):
        phone_number = (
            match.group(1).replace("-", "").replace(" ", "").replace("\n", "")
        )

        if len(phone_number) > 10:  # Check if country code is present
            return f"{phone_number[:-10]} {phone_number[-10:]}"
        else:
            return phone_number

    return None


def extract_summary_text(text_content: str) -> str | Any | None:
    """
    Extracts the summary text from the given text content.

    Args:
        text_content (str): The text content to extract the summary from.

    Returns:
        str | Any | None: The extracted summary text, or None if no summary is found.
    """
    email = extract_email(text_content)
    phone = extract_phone(text_content)
    links = re.finditer(LINK_PATTERN, text_content)
    links = [i.group(0) for i in links]
    if links:
        for link in links:
            text_content = text_content.replace(link, "<link masked>")

    try:
        if email and phone:
            text_content = text_content.replace(phone, "<phone no. masked>").replace(
                email, "<email masked>"
            )
        elif email:
            text_content = text_content.replace(email, "<email masked>")
        elif phone:
            text_content = text_content.replace(phone, "<phone no. masked>")
        else:
            text_content = text_content
    except Exception as e:
        print("Exception", e)

    match = SUMMARY_PATTERN.search(text_content.strip())
    summary = match[2].strip() if match else None
    summary = codecs.decode(summary, "unicode-escape") if summary else None

    # If a match is found, return the content after the first PROFILE paragraph
    return summary.replace('"\\"', "").replace('\\""', "") if summary else None


def extract_experience_duration(
    text: str,
) -> tuple[float, str] | tuple[Literal[0], Literal["0"]]:
    """
    Extracts the experience duration from the given text.

    Args:
        text (str): The text to extract the experience duration from.

    Returns:
        tuple[float, str] | tuple[Literal[0], Literal["0"]]: A tuple containing the numeric value
        and the duration string. If no match is found, a default tuple with values 0 and "0" is returned.
    """
    if match := EXPERIENCE_DURATION_PATTERN.search(text):
        numeric_value = float(match[1])
        duration_string = match[0].replace("\n", " ")
        return numeric_value, duration_string

    # Return a default value if no match is found
    return 0, "0"


def extract_experience_text(text_content: str) -> str | Any | None:
    """
    Extracts the experience text from the given text content.

    Args:
        text_content (str): The text content to extract the experience text from.

    Returns:
        str | Any | None: The extracted experience text, or None if no match is found.
    """
    email = extract_email(text_content)
    phone = extract_phone(text_content)
    try:
        if email and phone:
            text_content = text_content.replace(phone, "<phone no. masked>").replace(
                email, "<email masked>"
            )
        elif email:
            text_content = text_content.replace(email, "<email masked>")
        elif phone:
            text_content = text_content.replace(phone, "<phone no. masked>")
        else:
            text_content = text_content
    except Exception as e:
        print("Exception", e)

    # Define the regex pattern
    match = EXPERIENCE_TEXT_PATTERN.search(text_content)

    # If a match is found, return the content after the first PROFILE paragraph
    return match[2].strip() if match else None
