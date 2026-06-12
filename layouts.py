import os
import json
import read_json_script as rjs
import flet as ft

def main(page: ft.Page):
    page.title = "JSON Key Finder"
    page.window.width = 500
    page.window.height = 650
    
    # Use the clean built-in adaptive color scheme theme
    page.theme_mode = ft.ThemeMode.SYSTEM 

    # --- REWRITTEN CLEAN UI ELEMENTS ---
    file_dropdown = ft.Dropdown(
        label="Select Working File",
        options=[ft.dropdown.Option(key=str(k), text=f"{k}: {v}") for k, v in available_files.items()],
        expand=True # Stretches to fill the space
    )

    key_input = ft.TextField(
        label="Search Key", 
        hint_text="e.g., ID101",
        prefix_icon=ft.Icons.KEY, # Adds a small key icon inside the text field
        expand=True
    )

    result_output = ft.Text(
        value="Awaiting search query...", 
        size=15, 
        color=ft.Colors.ON_SURFACE_VARIANT
    )

    # --- LAYOUT CONTAINERS ---
    # Putting input controls inside a beautifully spaced card deck
    input_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([ft.Icon(ft.icons.SETTINGS_SYSTEM_DAYDREAM), ft.Text("Parameters", weight=ft.FontWeight.BOLD)]),
                file_dropdown,
                key_input,
            ], spacing=15)
        )
    )

    # Putting results inside a neat console box
    output_card = ft.Container(
        content=result_output,
        padding=15,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        border_radius=10,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        expand=True
    )

    submit_button = ft.FilledButton(
        text="Execute Search", 
        icon=ft.icons.SEARCH,
        on_click=button_clicked,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    # Add layouts seamlessly to the canvas
    page.add(
        ft.Text("JSON Key Lookup Tool", size=24, weight=ft.FontWeight.BOLD),
        input_card,
        ft.Row([submit_button], alignment=ft.MainAxisAlignment.END),
        ft.Text("Console Output", size=14, weight=ft.FontWeight.W_500),
        output_card
    )
