import json


def keep_only_title(json_file_path: str):
    with open(json_file_path, "r") as file:
        data = json.load(file)

    for item in data:
        title_value = item.get("title")
        item.clear()
        item["title"] = title_value

    with open(json_file_path, "w") as file:
        json.dump(data, file, indent=2)


# Usage example
keep_only_title("skills-collection.json")


def extract_titles(json_file_path):
    with open(json_file_path, "r") as file:
        data = json.load(file)

    titles = [{"title": item["title"]} for item in data if "title" in item]

    with open("output.json", "w") as output_file:
        json.dump(titles, output_file, indent=2)


extract_titles("skills-collection.json")
