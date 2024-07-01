import pandas as pd
from tqdm import tqdm

# Assuming your Excel file is in the same directory as this script
excel_file_path = "BNI Data all india.xlsx"
sheet_name = "india-members"

# Read the Excel file
df = pd.read_excel(excel_file_path, sheet_name=sheet_name)

# Extract the 'id' column
id_column = df["id"]

# Convert the 'id' column to a list and then to a dictionary
id_data = id_column.tolist()

# Save the data to a JSON file with tqdm progress bar
json_file_path = "uid_data.json"

# Create a tqdm instance with the total number of items
with tqdm(total=len(id_data), desc="Writing to JSON", unit="item") as pbar:
    # Open the file in write mode
    with open(json_file_path, "w") as json_file:
        json_file.write('{"id": [')

        # Loop through the 'id_data' list
        for i, item in enumerate(id_data):
            # Write the item to the file
            json_file.write(str(item))

            # Add a comma if it's not the last item
            if i < len(id_data) - 1:
                json_file.write(", ")

            # Update the progress bar
            pbar.update(1)

        # Complete the JSON structure
        json_file.write("]}")

# Print a newline after the progress bar is complete
print("\nWriting to JSON complete!")
