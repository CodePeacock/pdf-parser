"""
A Flask app with async tasks,
for uploading PDF file or URL of PDF file
and extracting information from it.
"""

import asyncio
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from operator import itemgetter
from typing import Any, Dict, Literal

import httpx
from flask import Flask, Response, jsonify, request
from flask_compress import Compress  # type: ignore
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from main_config import (
    NAME_PATTERN,
    URL_TO_FETCH_DESIGNATION,
    URL_TO_FETCH_SKILL,
    extract_email,
    extract_experience_duration,
    extract_experience_text,
    extract_phone,
    extract_summary_text,
)
from pdf_utils import extract_text_line_by_line

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
Compress(app)


class PdfProcessor:
    """
    A class that provides methods for downloading and processing PDF files.
    """

    @staticmethod
    async def download_pdf_from_url(
        pdf_url: str, local_path: str, timeout_seconds: int = 30
    ) -> None:
        """
        Downloads a PDF file from the given URL and saves it to the specified local path.

        Args:
            pdf_url (str): The URL of the PDF file to download.
            local_path (str): The local path where the downloaded PDF file will be saved.
            timeout_seconds (int, optional): The timeout value in seconds for the download request. Defaults to 30.

        Raises:
            httpx.HTTPStatusError: If the download request fails with a non-successful status code.
        """
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "GET", pdf_url, timeout=timeout_seconds
            ) as response:
                response.raise_for_status()
                with open(local_path, "wb") as local_pdf_file:
                    async for chunk in response.aiter_bytes():
                        local_pdf_file.write(chunk)

    @staticmethod
    async def process_pdf(
        pdf_url: str, filename: str
    ) -> dict[str, str | list[str] | None]:
        """
        Downloads a PDF file from the given URL, processes it, and extracts information from it.

        Args:
            pdf_url (str): The URL of the PDF file to process.
            filename (str): The name of the PDF file.

        Returns:
            dict[str, str | list[str] | None]: A dictionary containing the extracted information from the PDF.
                The dictionary has the following keys:
                - 'type': The type of the document.
                - 'content': The extracted elements from the PDF.
                - 'timestamp': The timestamp when the processing was performed.
        """
        local_pdf_path = os.path.join("resume-data", filename, f"{filename}.pdf")

        await PdfProcessor.download_pdf_from_url(pdf_url, local_pdf_path)
        elements = extract_text_line_by_line(local_pdf_path)
        return PdfProcessor.extract_information(elements)

    @staticmethod
    def extract_information(
        elements: list[str] | None,
    ) -> dict[str, str | list[str] | None]:
        """
        Extracts information from the given list of elements.

        Args:
            elements (list[str] | None): The list of elements to extract information from.

        Returns:
            dict[str, str | list[str] | None]: A dictionary containing the extracted information.
                The dictionary has the following keys:
                - 'type': The type of the document.
                - 'content': The extracted elements.
                - 'timestamp': The timestamp when the extraction was performed.
        """
        return {
            "type": "document",
            "content": elements,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def check_and_collect_skills(
    text_content: str, json_data: list[Any] | None
) -> list[Any] | None:
    """
    Check and collect skills from the given text content based on the provided JSON data.

    Args:
        text_content (str): The text content to search for skills.
        json_data (list[Any] | None): The JSON data containing skills information.

    Returns:
        list[Any] | None: A list of skills found in the text content, or None if no JSON data is provided.
    """
    title_getter = itemgetter("title")
    if json_data:
        return [
            title_getter(item)
            for item in json_data
            if re.search(
                r"\b{}\b".format(re.escape(title_getter(item))),
                text_content,
                re.IGNORECASE,
            )
        ]


def check_and_collect_designation_ids(
    text_content: str, json_data: list[Any] | None
) -> tuple[list[Any], Any | Literal[""]]:
    """
    Check and collect designation IDs based on the given text content and JSON data.

    Args:
        text_content (str): The text content to search for designations.
        json_data (list[Any] | None): The JSON data containing designation information.

    Returns:
        tuple[list[Any], list[Any], Any | Literal[""]]: A tuple containing the following:
            - sorted_designations (list[Any]): A list of sorted matching designations.
            - matching_designations_id (list[Any]): A list of _id values corresponding to the matching designations.
            - result_title (Any | Literal[""]): The result title, which is the first element of sorted_designations or an empty string if no matching designations are found.
    """
    title_getter = itemgetter("designation")

    # Extract all designations from the JSON data
    all_designations = [title_getter(item) for item in json_data]

    # Use list comprehensions for a more concise style
    matching_designations = [
        designation
        for designation in all_designations
        if re.search(
            r"\b{}\b".format(re.escape(designation)), text_content, re.IGNORECASE
        )
    ]

    # Sort the matching designations based on their appearance in the text
    sorted_designations = sorted(
        matching_designations,
        key=lambda designation: (
            min(
                (
                    match.start()
                    for match in re.finditer(
                        r"\b{}\b".format(re.escape(designation)),
                        text_content,
                        re.IGNORECASE,
                    )
                ),
                default=float("inf"),
            )
        ),
    )

    # Check if matching_designations list is not empty before accessing its first element
    result_title = sorted_designations[0] if sorted_designations else ""

    # Return the list of matching (_id, designation) tuples and the result title
    return sorted_designations, result_title


async def send_json_to_api(filename: str) -> Any:
    """
    Sends the extracted JSON data from the specified file to an API.

    Args:
        filename (str): The name of the file containing the JSON data.

    Returns:
        Any: The JSON data extracted from the file.
    """
    with open(f"{filename}_extracted_info.json", "r") as json_file:
        json_data = json.load(json_file)
    return json_data


async def save_url_as_json_async(url: str, output_file: str) -> list[Any] | None:
    """
    Fetches data from the given URL and saves it as a JSON file.

    Args:
        url (str): The URL to fetch the data from.
        output_file (str): The path to save the JSON file.

    Returns:
        list[Any] | None: The fetched data as a list of any type, or None if there was an error.

    Raises:
        httpx.RequestError: If there was an error fetching the data.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

            if response.status_code != 200:
                print(f"Error: Unexpected response status {response.status_code}")
                if os.path.exists(output_file):
                    with open(output_file, "r") as json_file:
                        data = json.load(json_file)
                        print(f"Data loaded from local {output_file}")
                        # Remove duplicates based on hash
                        data = remove_duplicates(data=data)
                    return data

                else:
                    print(f"Error: Local {output_file} not found")
                    return None
            response.raise_for_status()

            with open(output_file, "wb") as json_file:
                json_file.write(response.content)
                hash_md5 = hashlib.md5()
                hash_md5.update(response.content)
                downloaded_hash = hash_md5.hexdigest()

            if os.path.exists(output_file):
                with open(output_file, "rb") as local_json_file:
                    hash_md5 = hashlib.md5()
                    hash_md5.update(local_json_file.read())
                    local_hash = hash_md5.hexdigest()

            else:
                local_hash = None

            if downloaded_hash == local_hash:
                with open(output_file, "r") as json_file:
                    data = json.load(json_file)
                    print(f"Data loaded from local {output_file}")
                    # Remove duplicates based on hash
                    data = remove_duplicates(data)
                return data

            data = response.json()

            with open(output_file, "w") as json_file:
                json.dump(data, json_file, indent=2)

            print(f"Data saved successfully to {output_file}")
            # Remove duplicates based on hash
            data = remove_duplicates(data)
            return data
    except httpx.RequestError as e:
        print(f"Error fetching data: {e}")
    return None


def remove_duplicates(data) -> list[Any]:  # type: ignore
    """
    Remove duplicates from a list of items.

    Args:
        data: A list of items.

    Returns:
        A new list with duplicates removed, while maintaining the original order.
    """
    unique_items = set()  # type: ignore
    result = []

    for item in data:  # type: ignore
        item_hash = hashlib.md5(json.dumps(item, sort_keys=True).encode()).hexdigest()
        if item_hash not in unique_items:
            unique_items.add(item_hash)  # type: ignore
            result.append(item)  # type: ignore

    return result  # type: ignore


def extract_name(
    text_content: str, json_data: list[Any] | None
) -> (
    tuple[str | Any, str | Any]
    | tuple[str, Literal[""]]
    | tuple[Literal[""], Literal[""]]
):
    (
        designations,
        _,
    ) = check_and_collect_designation_ids(text_content, json_data)

    email = extract_email(text_content)

    # Titlecase the designation and add to the list
    cleaned_text = text_content
    for item_ in designations:
        cleaned_text = cleaned_text.replace(item_, "").replace("–", "").strip()
        if email:
            cleaned_text = cleaned_text.replace(email, "").replace(":", "").strip()

        cleaned_text = "\n".join(line.strip() for line in cleaned_text.split("\n"))

    # Search for the pattern in the cleaned text
    cleaned_text = re.sub(r"\bLinkedIn\b", "", cleaned_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(
        r"\b\w+\.vercel\.app\b", "", cleaned_text, flags=re.IGNORECASE
    )
    cleaned_text = cleaned_text.replace("|", " ").replace("Resume", "")
    # print(cleaned_text)
    phone = extract_phone(cleaned_text)
    if phone:
        cleaned_text = cleaned_text.replace(phone, "").replace("+", "").strip()
    match = NAME_PATTERN.search(string=cleaned_text)

    # Check if conditions are met
    if (
        match
        and match[1]
        and match[2]
        and len(match[1].strip()) > 2
        and len(match[1].strip()) < 50
        and len(match[2].strip()) > 2
    ):
        # Return name and surname if both groups are more than 2 letters
        name = match[1].strip()
        surname = match[2].strip() if "\n" not in match[2] else ""
        return name, surname
    elif match and match[1] and len(match[2].strip()) <= 2:
        # Return name if group 1 is not None and group 2 is less than 2 letters
        name = match[1].strip()
        return (
            f"{name}{match[2].strip() if match[2] and len(match[2].strip()) <= 2 else ''}",
            "",
        )
    else:
        return "", ""


def remove_unrecognized_characters(text: str | Any | None) -> str | None:
    """
    Removes unrecognized characters from the given text.

    Args:
        text (str | Any | None): The text to process.

    Returns:
        str | None: The processed text with unrecognized characters removed, or None if the input text is None.
    """
    if text:
        return re.sub(r"[^\x00-\x7F]+", " ", text).replace("\n", " ").strip()


async def check_titles_and_extract_info(
    text_file_path: str,
    json_skills: list[Any] | None,
    json_designations: list[Any] | None,
) -> None:
    """
    Check titles and extract information from a text file.

    Args:
        text_file_path (str): The path to the text file.
        json_skills (list[Any] | None): A list of skills in JSON format.
        json_designations (list[Any] | None): A list of designations in JSON format.

    Returns:
        None
    """
    try:
        with open(text_file_path, "r", encoding="utf-8") as text_file:
            file_content = text_file.read()
            "Summary Adaptable Computer Engineer With Extensive Experience In Development Using React"

            firstName, lastName = extract_name(
                text_content=file_content, json_data=json_designations
            )
            # print(firstName, lastName)
            # use fstring to combine firstName and lastName
            name = f"{firstName} {lastName}".strip().replace("\n", " ")
            email = extract_email(file_content)
            phone = extract_phone(file_content)
            summary = extract_summary_text(file_content)
            amount_of_experience, duration_string = extract_experience_duration(
                file_content
            )
            skills = check_and_collect_skills(file_content, json_skills)

            (
                designations,
                designation_title,
            ) = check_and_collect_designation_ids(file_content, json_designations)
            work_experience = extract_experience_text(file_content)

            with open(f"{text_file_path}_extracted_info.json", "w") as json_file:
                json.dump(
                    {
                        "name": name.title() or "",
                        "email": email or "",
                        "phone": phone or "",
                        "skills": sorted(list(set(skills))) or [],  # type: ignore
                        "designation": designations or [],
                        "experience": [
                            {
                                # return first element in set, if empty return empty list
                                "title": designation_title or "",
                                "amount_of_experience": amount_of_experience or 0,
                                "duration_string": remove_unrecognized_characters(
                                    duration_string
                                )
                                or "",
                                "summary": remove_unrecognized_characters(summary)
                                or "",
                            }
                        ],
                        "work_experience": remove_unrecognized_characters(
                            work_experience
                        )
                        or "",
                    },
                    json_file,
                    indent=2,
                    sort_keys=True,
                )
            # print(
            #     f"Name: {name}, Email: {email}, Phone: {phone}, Skills: {skills}, Summary: {remove_unrecognized_characters(summary)}, designation: {next(iter(set(designation)), '')}, Experience: {years_of_experience}, Work Experience: {remove_unrecognized_characters(work_experience)}"
            # )
    except FileNotFoundError:
        print(f"Error: File '{text_file_path}' not found.")


def process_uploaded_file(file: FileStorage) -> tuple[list[str] | None, str]:
    """
    Process the uploaded file and extract text line by line.

    Args:
        file (FileStorage): The uploaded file.

    Returns:
        tuple[list[str] | None, str]: A tuple containing the extracted elements as a list of strings
        and the filename of the uploaded file.
    """
    filename = secure_filename(file.filename or "no_file")
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)  # type:ignore
    file.save(file_path)  # type:ignore

    elements = extract_text_line_by_line(file_path)

    return elements, filename


@app.route("/extract", methods=["POST"])
async def extract_data() -> (
    tuple[Response, Literal[404]]
    | Any
    | tuple[Response, Literal[400]]
    | tuple[Response, Literal[500]]
):
    """
    Extracts data from either a file upload or a PDF URL.

    Returns:
        A tuple containing the response and status code:
        - If successful, returns a tuple with the response and status code 200.
        - If the file is not found, returns a tuple with the response and status code 404.
        - If no file or PDF URL is provided, returns a tuple with the response and status code 400.
        - If there is an error fetching or processing the PDF, returns a tuple with the response and status code 500.
    """
    try:
        if "file" in request.files:
            file: FileStorage = request.files["file"]
            file_name = file.filename.strip(".pdf") if file.filename else "no_file"
            os.makedirs(f"resume-data/{file_name}", exist_ok=True)
            elements, filename = process_uploaded_file(file)  # type:ignore

            extracted_data = PdfProcessor.extract_information(elements)
            text_file_path = await extract_text(file_name, extracted_data)

            if not os.path.exists(f"{text_file_path}_extracted_info.json"):
                return jsonify({"error": "File not found"}), 404

            return await send_json_to_api(filename=text_file_path)

        elif "pdf_url" in request.form:
            pdf_url = request.form["pdf_url"]
            file_name = os.path.basename(pdf_url)
            os.makedirs(f"resume-data/{file_name}", exist_ok=True)

            extracted_data = await PdfProcessor.process_pdf(pdf_url, filename=file_name)

            text_file_path = await extract_text(file_name, extracted_data)

            if not os.path.exists(f"{text_file_path}_extracted_info.json"):
                return jsonify({"error": "File not found"}), 404

            return await send_json_to_api(filename=text_file_path)
        else:
            return jsonify({"error": "No file or PDF URL provided"}), 400

    except httpx.RequestError as e:
        return jsonify({"error": f"Error fetching or processing PDF: {str(e)}"}), 500


async def extract_text(file_name: str, extracted_data: Dict[Any, Any]) -> str:
    """
    Extracts text from the given extracted_data and saves it to a text file.

    Args:
        file_name (str): The name of the file.
        extracted_data (Dict[Any, Any]): The extracted data containing the text.

    Returns:
        str: The file path of the saved text file.
    """
    text: str = extracted_data["content"]
    # text = PdfProcessor.clean_unicode(text=text)

    pdf_name = f"resume-data/{file_name}/{file_name}.txt"

    with open(pdf_name, "w", encoding="utf-8", errors="replace") as f:
        for line in text:
            line = line.replace(
                "", ""
            )  # Replace dot symbol not recognized by the system
            line = remove_unrecognized_characters(text=line)
            if line is not None:
                f.write(line + "\n")

    output_file_path_skill = "skills-collection.json"
    output_file_path_designation = "designations-collection.json"
    text_file_path = pdf_name
    acquired_skill_data = await save_url_as_json_async(
        URL_TO_FETCH_SKILL, output_file_path_skill
    )
    skill_titles = (
        [item["title"] for item in acquired_skill_data] if acquired_skill_data else []
    )

    acquired_designation_data = None
    while acquired_designation_data is None:
        acquired_designation_data = await save_url_as_json_async(
            URL_TO_FETCH_DESIGNATION, output_file_path_designation
        )
        if acquired_designation_data is None:
            print("Waiting for acquired_designation_data...")
            await asyncio.sleep(2)  # Add a short delay before retrying

    designation_titles = [
        item.get("designation", "") for item in acquired_designation_data
    ]

    if skill_titles and designation_titles:
        await asyncio.gather(
            asyncio.create_task(
                check_titles_and_extract_info(
                    text_file_path,
                    acquired_skill_data,
                    json_designations=acquired_designation_data,
                )
            ),
        )

    return text_file_path


if __name__ == "__main__":
    app.run(
        port=10000,
        reloader_type="watchdog" if os.name == "nt" else "stat",
        use_reloader=True,
        threaded=True,
    )
