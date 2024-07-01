import json


def remove_id_key(input_file, output_file):
    """
    Remove the "id" key from each entry in the input JSON file and save the modified data to the output file.

    Args:
        input_file (str): The path to the input JSON file.
        output_file (str): The path to the output JSON file.

    Raises:
        Exception: If there is an error while processing the files.

    """
    try:
        with open(input_file, "r") as json_file:
            data = json.load(json_file)

        # Remove the "id" key from each entry
        for item in data:
            item.pop("_id", None)

        with open(output_file, "w") as json_file:
            json.dump(data, json_file, indent=2)

        print(f"'id' key removed. Modified data saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")


# Example usage
input_json_file = "output.json"  # Replace with your input file
output_json_file = "output.json"  # Replace with your desired output file

remove_id_key(input_json_file, output_json_file)
