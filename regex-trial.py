def extract_name(text_content, json_data: list):
    designation = check_and_collect_designation(text_content, json_data)

    cleaned_text = text_content.replace(designation[0], " ").replace("–", "").strip()

    # Define the regex pattern for extracting the name
    name_pattern = re.compile(
        r"^(?:.*?(?:Mrs\.|Mr\.|Miss|Ms\.|(?:Name:))?\s*([A-Za-z]+)\s*([A-Za-z]+(?: [A-Za-z]+)*))",
    )

    # Search for the pattern in the cleaned text
    match = name_pattern.search(string=cleaned_text)

    # Check if a match is found
    if match:
        # Access the matches using the provided structure
        matches = [
            {
                "content": match.group(0),
                "isParticipating": True,
                "groupNum": i,
                "startPos": match.start(i),
                "endPos": match.end(i),
            }
            for i in range(match.lastindex + 1)
        ]

        return matches