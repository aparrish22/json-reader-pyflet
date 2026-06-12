import json
import read_json_script as rjs
import flet as ft


def collect_json_keys(data, path="$"):
    """Return {display_path: value} for every JSON key."""
    keys = {}

    if isinstance(data, dict):
        for key, value in data.items():
            key_path = f"{path}[{json.dumps(str(key))}]"
            keys[key_path] = value
            keys.update(collect_json_keys(value, key_path))

    elif isinstance(data, list):
        for index, value in enumerate(data):
            keys.update(collect_json_keys(value, f"{path}[{index}]"))

    return keys


def main(page: ft.Page):
    page.title = "JSON Key Finder"
    page.window.width = 500
    page.window.height = 650
    page.padding = 20
    page.theme_mode = ft.ThemeMode.SYSTEM

    available_files = rjs.get_files_dict()
    current_data = None
    available_key_paths = {}

    title = ft.Text(
        "JSON Key Lookup Tool",
        size=24,
        weight=ft.FontWeight.BOLD,
    )

    key_input = ft.TextField(
        label="Enter Key to Search",
        hint_text="e.g., customer_id",
        prefix_icon=ft.Icons.KEY,
        expand=True,
    )

    key_list = ft.Dropdown(
        label="Select an Available Key",
        hint_text="Choose a JSON key",
        options=[],
        expand=True,
        visible=False,
    )

    def change_key_mode(e):
        manual_mode = key_mode.value == "manual"
        key_input.visible = manual_mode
        key_list.visible = not manual_mode
        page.update()

    key_mode = ft.RadioGroup(
        value="manual",
        content=ft.Row(
            controls=[
                ft.Radio(value="manual", label="Enter a key"),
                ft.Radio(value="dropdown", label="Browse keys"),
            ]
        ),
        on_change=change_key_mode,
    )

    result_output = ft.Text(
        value="Select a JSON file to begin.",
        color=ft.Colors.ON_SURFACE_VARIANT,
        expand=True,
    )

    def load_json_keys(e):
        nonlocal current_data, available_key_paths

        key_list.value = None
        key_list.options = []
        available_key_paths = {}
        current_data = None

        if not file_dropdown.value:
            page.update()
            return

        try:
            selected_file = available_files[int(file_dropdown.value)]
            file_path = f"{rjs.data_dir}/{selected_file}"

            if not rjs.verify_json(file_path):
                raise ValueError("Failed to verify JSON file")

            current_data = rjs.read_file(file_path)
            available_key_paths = collect_json_keys(current_data)

            key_list.options = [
                ft.dropdown.Option(key=path, text=path)
                for path in sorted(available_key_paths)
            ]

            result_output.value = (
                f"Loaded {len(available_key_paths)} keys from "
                f"{selected_file}."
            )
            result_output.color = ft.Colors.ON_SURFACE_VARIANT

        except Exception as err:
            result_output.value = f"Error loading file: {err}"
            result_output.color = ft.Colors.RED

        page.update()

    file_dropdown = ft.Dropdown(
        label="1. Choose a JSON File",
        options=[
            ft.dropdown.Option(key=str(key), text=f"{key}: {filename}")
            for key, filename in available_files.items()
        ],
        on_select=load_json_keys,
        expand=True,
    )

    def process_data(e):
        if current_data is None:
            result_output.value = "Error: Please select a file first!"
            result_output.color = ft.Colors.RED
            page.update()
            return

        try:
            if key_mode.value == "manual":
                user_key = key_input.value.strip()

                if not user_key:
                    raise ValueError("Please enter a key to search for")

                results, duplicates = rjs.find_nested_key(
                    current_data,
                    user_key,
                )

                result_output.value = (
                    f"Search key: {user_key}\n"
                    f"Results: {results}\n"
                    f"Duplicates: {duplicates}"
                )

            else:
                selected_path = key_list.value

                if not selected_path:
                    raise ValueError("Please select a key")

                value = available_key_paths[selected_path]

                result_output.value = (
                    f"Path: {selected_path}\n"
                    f"Value:\n{json.dumps(value, indent=2, default=str)}"
                )

            result_output.color = ft.Colors.GREEN

        except Exception as err:
            result_output.value = f"Error: {err}"
            result_output.color = ft.Colors.RED

        page.update()

    submit_button = ft.ElevatedButton(
        content="Search File",
        icon=ft.Icons.SEARCH,
        on_click=process_data,
        width=450,
    )

    page.add(
        title,
        ft.Divider(),
        file_dropdown,
        ft.Text("2. Choose Search Method"),
        key_mode,
        key_input,
        key_list,
        ft.Container(height=10),
        submit_button,
        ft.Container(height=20),
        ft.Text("Output:", weight=ft.FontWeight.BOLD),
        ft.Container(
            content=result_output,
            padding=15,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            width=450,
        ),
    )


ft.app(target=main)
