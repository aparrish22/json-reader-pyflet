import os
import json
import flet as ft

SUBFOLDER = "data_files"

def get_json_files_dict():
    """Scans the subfolder and returns a dictionary of {integer_key: filename}."""
    files_dict = {}
    if os.path.exists(SUBFOLDER):
        # Enumerate gives us clean sequential numbers (1, 2, 3...)
        for i, file in enumerate(os.listdir(SUBFOLDER)):
            if file.endswith(".json"):
                files_dict[i + 1] = file
    return files_dict

def extract_all_keys(data, current_prefix=""):
    """
    Recursively extracts all keys from a dictionary, including nested keys.
    Returns a list of strings like ['name', 'address.city', 'address.zip']
    """
    keys_list = []
    if isinstance(data, dict):
        for k, v in data.items():
            full_key = f"{current_prefix}.{k}" if current_prefix else str(k)
            keys_list.append(full_key)
            # If the value is another dictionary, look deeper inside it
            if isinstance(v, dict):
                keys_list.extend(extract_all_keys(v, current_prefix=full_key))
    return keys_list

def main(page: ft.Page):
    page.title = "JSON Nested Key Explorer"
    page.window.width = 500
    page.window.height = 750
    page.padding = 20

    available_files = get_json_files_dict()

    # --- UI ELEMENTS ---
    title = ft.Text("JSON Key Lookup Tool", size=24, weight=ft.FontWeight.BOLD)
    
    # Dropdown for selecting the file
    file_dropdown = ft.Dropdown(
        label="1. Choose a JSON File",
        options=[ft.dropdown.Option(key=str(k), text=f"{k}: {v}") for k, v in available_files.items()],
        width=450
    )

    # NEW: Dropdown for keys, starts empty and disabled
    key_dropdown = ft.Dropdown(
        label="2. Choose a Key (Populated from File)",
        options=[],
        width=450,
        disabled=True
    )

    result_output = ft.Text(
        value="Select a file to begin.", 
        size=16, 
        color=ft.Colors.BLUE_GREY_400
    )

    # --- DROP_DOWN AUTO UPDATE LOGIC ---
    def on_file_selected(e):
        """Triggers automatically when a user clicks a file from the dropdown."""
        if not file_dropdown.value:
            return

        selected_key_int = int(file_dropdown.value)
        selected_filename = available_files[selected_key_int]
        file_path = os.path.join(SUBFOLDER, selected_filename)

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # 1. Grab all regular and nested keys from our file data
            all_extracted_keys = extract_all_keys(data)

            # 2. LIST COMPREHENSION: Convert the raw keys list into Flet Dropdown Options
            key_dropdown.options = [ft.dropdown.Option(k) for k in all_extracted_keys]
            
            # 3. Enable the key dropdown and reset any old selected value
            key_dropdown.disabled = False
            key_dropdown.value = None
            result_output.value = f"Loaded {len(all_extracted_keys)} keys from {selected_filename}."
            result_output.color = ft.Colors.BLUE_200

        except Exception as err:
            result_output.value = f"Failed to load keys: {str(err)}"
            result_output.color = ft.Colors.RED
            key_dropdown.disabled = True
            key_dropdown.options = []

        page.update()

# TODO .on_change doesnt exist
    # Hook up the automatic action event to our first dropdown
    file_dropdown.on_change = on_file_selected

    # --- SUBMIT BUTTON SEARCH LOGIC ---
    def process_data(e):
        if not file_dropdown.value or not key_dropdown.value:
            result_output.value = "Error: Please select both a file and a key!"
            result_output.color = ft.Colors.RED
            page.update()
            return

        selected_key_int = int(file_dropdown.value)
        selected_filename = available_files[selected_key_int]
        file_path = os.path.join(SUBFOLDER, selected_filename)
        
        chosen_key_path = key_dropdown.value

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Dig down into the nested dictionary using the dot notation path
            # (e.g., matching "address.city")
            current_layer = data
            for part in chosen_key_path.split('.'):
                current_layer = current_layer[part]
            
            result_output.value = f"Success!\n[{chosen_key_path}] -> {current_layer}"
            result_output.color = ft.Colors.GREEN

        except Exception as err:
            result_output.value = f"System Error reading data path: {str(err)}"
            result_output.color = ft.Colors.RED
        
        page.update()

    submit_button = ft.ElevatedButton(
        # TODO no error exixsts 
        text="Fetch Value", 
        icon=ft.Icons.SEARCH,
        on_click=process_data,
        width=450
    )

    # --- ADD TO PAGE WITH EXPANDED OUTPUT BOX ---
    page.add(
        title,
        ft.Divider(),
        file_dropdown,
        ft.Container(height=5),
        key_dropdown,
        ft.Container(height=10),
        submit_button,
        ft.Container(height=20),
        ft.Text("Console Output:", weight=ft.FontWeight.BOLD),
        ft.Container(
            content=ft.Column([result_output], scroll=ft.ScrollMode.AUTO),
            padding=15,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            width=450,
            bgcolor=ft.Colors.GREY_50,
            expand=True # The output box stretches down beautifully
        )
    )

ft.app(target=main)
