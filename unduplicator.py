import json


def remove_duplicates_and_save(file_path):
    with open(file_path, "r") as file:
        json_data = json.load(file)

    unique_designations = set()
    unique_json_data = []

    for item in json_data:
        designation = item.get("title")

        # Check if the designation is not in the set (not a duplicate)
        if designation not in unique_designations:
            unique_designations.add(designation)
            unique_json_data.append(item)

    with open(file_path, "w") as file:
        json.dump(unique_json_data, file, indent=2)


remove_duplicates_and_save("output.json")
