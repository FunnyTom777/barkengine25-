import dearpygui.dearpygui as dpg
import yaml
import importlib
import os
import json

# --- Import the game module dynamically ---
game = importlib.import_module("game")

# --- Load commands.yaml ---
with open("commands.yaml", "r") as f:
    COMMANDS = yaml.safe_load(f)

# --- Load or create settings ---
SETTINGS_FILE = "ui_settings.json"
DEFAULT_SETTINGS = {
    "gui_scale": 1.0,
    "theme": "Dark",
    "window_width": 800,
    "window_height": 600
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

# --- Chat/console state ---
chat_log = []
settings = load_settings()

# --- Theme colors ---
COLORS = {
    "command": (51, 255, 51, 255),    # Green for commands
    "chat": (255, 255, 255, 255),     # White for chat
    "system": (179, 179, 179, 255),   # Gray for system messages
    "error": (255, 77, 77, 255)       # Red for errors
}

def set_theme():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 5, 5)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 4, 4)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (128, 128, 128, 255))
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 12)
            
    dpg.bind_theme(global_theme)


def handle_input(sender, app_data):
    if not app_data.strip():
        return
    
    text = app_data.strip()
    if text.startswith("/"):
        # Handle as command
        handle_command(text[1:])  # Remove the / prefix
    else:
        # Handle as chat message
        chat_log.append(f"> {text}")
    
    # Clear input
    dpg.set_value("input_text", "")
    
def update_chat_window():
    # Clear existing items
    if dpg.does_item_exist("chat_window"):
        dpg.delete_item("chat_window", children_only=True)
        
    # Add messages with appropriate colors
    for line in chat_log:
        if line.startswith("> /"):  # Command
            dpg.add_text(line, parent="chat_window", color=COLORS["command"])
        elif line.startswith("> "):  # Chat message
            dpg.add_text(line, parent="chat_window", color=COLORS["chat"])
        elif line.startswith("Error:"):  # Error message
            dpg.add_text(line, parent="chat_window", color=COLORS["error"])
        else:  # System/response message
            dpg.add_text(line, parent="chat_window", color=COLORS["system"])
    
    # Auto-scroll to bottom
    dpg.set_y_scroll("chat_window", -1.0)

def save_scale_callback(sender, app_data):
    settings["gui_scale"] = app_data
    save_settings(settings)
    dpg.set_global_font_scale(app_data)

def reset_settings():
    settings.update(DEFAULT_SETTINGS)
    save_settings(settings)
    dpg.set_global_font_scale(settings["gui_scale"])
    dpg.set_value("scale_slider", settings["gui_scale"])

def toggle_settings_window(sender, app_data):
    # Only toggle settings if chat input is not focused
    if not dpg.is_item_focused("input_text"):
        if dpg.is_item_visible("settings_window"):
            dpg.hide_item("settings_window")
        else:
            dpg.show_item("settings_window")

def main():
    # Initialize Dear PyGui
    dpg.create_context()
    dpg.create_viewport(title="Game Console", width=settings["window_width"], height=settings["window_height"])
    dpg.setup_dearpygui()

    # Set up the theme
    set_theme()
    
    # Apply saved scale
    dpg.set_global_font_scale(settings["gui_scale"])

    # Create settings window (hidden by default)
    with dpg.window(label="Settings", width=300, height=150, pos=[50, 50],
                   show=False, tag="settings_window"):
        dpg.add_slider_float(label="UI Scale", default_value=settings["gui_scale"],
                           min_value=0.5, max_value=3.0, callback=save_scale_callback,
                           tag="scale_slider")
        dpg.add_separator()
        dpg.add_button(label="Reset to Default", callback=reset_settings)
        dpg.add_button(label="Close", callback=lambda: dpg.hide_item("settings_window"))

    # Create main window
    with dpg.window(label="Chat/Console", width=settings["window_width"]-20,
                   height=settings["window_height"]-20, pos=[10, 10],
                   no_close=True, no_move=True):
        
        # Add chat window with scrolling
        with dpg.child_window(width=-1, height=-60, tag="chat_window"):
            pass  # Messages will be added dynamically
            
        # Add input field
        dpg.add_input_text(width=-1, tag="input_text", on_enter=True, callback=handle_input)
        
        # Keyboard shortcut for settings
        with dpg.handler_registry():
            dpg.add_key_press_handler(key=dpg.mvKey_S, callback=toggle_settings_window)

    # Show viewport
    dpg.show_viewport()

    # Set up window resize handling
    def save_window_size(sender, app_data):
        settings["window_width"] = app_data[0]
        settings["window_height"] = app_data[1]
        save_settings(settings)
        
    dpg.set_viewport_resize_callback(save_window_size)

    # Main loop
    while dpg.is_dearpygui_running():
        # Update chat messages
        update_chat_window()
        
        # Focus on input if empty and nothing else is focused
        input_text = dpg.get_value("input_text")
        if not input_text and not dpg.is_item_focused("input_text"):
            dpg.focus_item("input_text")
            
        dpg.render_dearpygui_frame()

    # Cleanup
    dpg.destroy_context()


def handle_command(text):
    chat_log.append(f"> /{text}")  # Show command with prefix in log
    
    # Split command and arguments
    parts = text.split()
    command = parts[0].lower() if parts else ""
    
    # Handle built-in commands first
    if command == "clear":
        chat_log.clear()
        return
    elif command == "help":
        chat_log.append("Available commands:")
        chat_log.append("  /help - Show this help message")
        chat_log.append("  /clear - Clear the chat")
        chat_log.append("  Type without / to chat")
        chat_log.append("Game commands:")
        for cmd in sorted(COMMANDS.keys()):
            chat_log.append(f"  /{cmd}")
        return
        
    # Handle game commands
    if command in COMMANDS:
        func_name = COMMANDS[command]
        func = getattr(game, func_name, None)
        if func:
            try:
                # Pass any additional arguments
                args = []
                if len(parts) > 1:
                    for arg in parts[1:]:
                        # Try to convert to number if possible
                        try:
                            if '.' in arg:
                                args.append(float(arg))
                            else:
                                args.append(int(arg))
                        except ValueError:
                            args.append(arg)
                
                result = func(*args) if args else func()
                if result is not None:
                    chat_log.append(str(result))
            except Exception as e:
                chat_log.append(f"Error: {str(e)}")
        else:
            chat_log.append(f"Error: Command '{command}' is configured but function '{func_name}' not found")
    else:
        chat_log.append(f"Unknown command: '{command}'. Type /help for available commands")


if __name__ == "__main__":
    main()
