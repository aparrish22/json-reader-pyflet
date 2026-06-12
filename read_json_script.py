import os
import json
from pathlib import Path

script_dir = Path(__file__).resolve().parent
search_path = str(script_dir)
data_dir = script_dir / "data"

def read_json_script():

    files_dict = get_files_dict()
    if not files_dict:
        print("There are no files to read!")
        exit(0) 
    total_files = 0

    print("--- Choose a json file to read (type the number) ---")
    for k,v in files_dict.items():
        print(f"{k}: {v}")
        total_files += 1
    user_input = input().strip()
    if not user_input:
        print("That's not a valid input! Out of my house!")
        exit(0)
    elif user_input == 0 or int(user_input) > total_files:
        print("That's not a valid input! Out of my yard!!")
        exit(0)
    key_input = int(user_input)
    the_file = data_dir / files_dict[key_input]
    verified = verify_json(the_file)
    if not verified:
        print("Out of my house once more!")
        exit(0)
    print(f"/{files_dict[key_input]} has been verified!")
    print(f"Reading /{files_dict[key_input]}...")
    json_content = read_file(the_file)

    target_key = "Sell_to_Customer_No"
    
    traveler_list, duplicate_set = find_nested_key(json_content, target_key)
    print("List of travelers!:")
    print(traveler_list)
    print("Let's check for any duplicates:")
    print(duplicate_set)

def find_nested_key(json: dict, target: str) -> tuple:
    all_travelers = []
    duplicate_travelers = set()  # Sets only store unique items
    # 2. Define the inner helper function to do the deep search
    def search(json_c):
        if isinstance(json_c, dict):
            for key, value in json_c.items():
                if key == target:
                    if value in all_travelers:
                        duplicate_travelers.add(value)
                    all_travelers.append(value)
                else:
                    search(value)
        elif isinstance(json_c, list):
            for item in json_c:
                search(item)

    # 3. Run the search
    search(json)

    # 4. Return both the list and the set together
    return all_travelers, duplicate_travelers  

def check_for_duplicates_in_json(json: dict) -> bool:

    for k,v in json.items():
        print(k["Traveler_No"])
    
    return False
    
def get_files_dict() -> dict:
    files = dict()
    folder = script_dir / "data"
    count = 1
    for file in folder.glob("*.json"):
        files[count] = file.name
        count += 1
    return files

def read_file(file_path: str) -> dict: # returns a json object {} or {content}
    """ reads & parses the JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            print("Loading File...")
            return json.load(file)
    except json.JSONDecodeError:
        print("Error: The file is not valid JSON")
        return {}
    except Exception as ex:
        print(f"An unexpected error occured: {ex}")
        return {}

def verify_json(file_path: str, max_size_mb: float = 5.0) -> bool:
    """Checks if the file exists and is under the safe size limit."""

    max_bytes = max_size_mb * 1024 * 1024

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)

    if file_size > max_bytes:
        print(f"WARNING: File is too large! ({file_size / (1024 * 1024):.2f} MB)")
        return False
    
    return True
# end of verify json

