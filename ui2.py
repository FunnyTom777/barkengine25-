

# BarkEngine25 Control Panel using DearPyGui
import dearpygui.dearpygui as dpg # type: ignore
import os
import dependencies
import modstuff

active_user = None
login_error = ""
create_error = ""

def try_login(sender, app_data, user_data):
    global active_user, login_error
    username = dpg.get_value("##loginuser")
    password = dpg.get_value("##loginpass")
    if dependencies.authenticateuser(username, password):
        active_user = username
        login_error = ""
        dpg.set_value("##loginerror", "")
        dpg.configure_item("Login Window", show=False)
        dpg.configure_item("Main Panel", show=True)
        dpg.set_value("##activeuser", active_user)
    else:
        login_error = "Invalid username or password."
        dpg.set_value("##loginerror", login_error)

def try_create(sender, app_data, user_data):
    global active_user, create_error
    username = dpg.get_value("##createuser")
    password = dpg.get_value("##createpass")
    if not username or not password:
        create_error = "Username and password required."
        dpg.set_value("##createerror", create_error)
        return
    dependencies.createuser(username, password)
    active_user = username
    create_error = ""
    dpg.set_value("##createerror", "User created! You are now logged in.")
    dpg.configure_item("Create Window", show=False)
    dpg.configure_item("Main Panel", show=True)
    dpg.set_value("##activeuser", active_user)

def show_create(sender, app_data, user_data):
    dpg.configure_item("Login Window", show=False)
    dpg.configure_item("Create Window", show=True)

def show_login(sender, app_data, user_data):
    dpg.configure_item("Create Window", show=False)
    dpg.configure_item("Login Window", show=True)

def reload_mods(sender, app_data, user_data):
    dependencies.loadmods()
    dpg.configure_item("##modlist", items=[f"{m.get('name','Unknown')} (ID: {m.get('modId','???')})" for m in modstuff.load_mods_from_folder()])

def show_config(sender, app_data, user_data):
    config = dependencies.CONFIG
    dpg.set_value("##configtext", "\n".join([f"{k}: {v}" for k,v in config.items()]))
    dpg.configure_item("Config Window", show=True)

def hide_config(sender, app_data, user_data):
    dpg.configure_item("Config Window", show=False)

def show_about(sender, app_data, user_data):
    dpg.configure_item("About Window", show=True)

def hide_about(sender, app_data, user_data):
    dpg.configure_item("About Window", show=False)


dpg.create_context()

with dpg.window(label="Login Window", tag="Login Window", width=400, height=250, no_resize=True, no_collapse=True):
    dpg.add_text("BarkEngine25 Login")
    dpg.add_input_text(label="Username", tag="##loginuser")
    dpg.add_input_text(label="Password", tag="##loginpass", password=True)
    dpg.add_button(label="Login", callback=try_login)
    dpg.add_same_line()
    dpg.add_button(label="Create Account", callback=show_create)
    dpg.add_text("", tag="##loginerror", color=[255,0,0])

with dpg.window(label="Create Window", tag="Create Window", width=400, height=250, no_resize=True, no_collapse=True, show=False):
    dpg.add_text("Create BarkEngine25 Account")
    dpg.add_input_text(label="Username", tag="##createuser")
    dpg.add_input_text(label="Password", tag="##createpass", password=True)
    dpg.add_button(label="Create", callback=try_create)
    dpg.add_same_line()
    dpg.add_button(label="Back to Login", callback=show_login)
    dpg.add_text("", tag="##createerror", color=[255,0,0])

with dpg.window(label="Main Panel", tag="Main Panel", width=600, height=500, show=False, no_resize=True, no_collapse=True):
    dpg.add_text("Welcome to BarkEngine25!")
    dpg.add_separator()
    dpg.add_text("Active User: ", color=[0,255,0])
    dpg.add_same_line()
    dpg.add_text("", tag="##activeuser")
    dpg.add_separator()
    config = dependencies.CONFIG
    dpg.add_text(f"Mod Loading: {'Disabled' if config.get('disablemodload') else 'Enabled'}")
    dpg.add_button(label="Reload Mods", callback=reload_mods)
    dpg.add_same_line()
    dpg.add_button(label="Show Config", callback=show_config)
    dpg.add_same_line()
    dpg.add_button(label="About", callback=show_about)
    dpg.add_separator()
    dpg.add_text("Loaded Mods:")
    mods = modstuff.load_mods_from_folder()
    dpg.add_listbox(tag="##modlist", items=[f"{m.get('name','Unknown')} (ID: {m.get('modId','???')})" for m in mods], num_items=8, width=400)

with dpg.window(label="Config Window", tag="Config Window", width=400, height=300, show=False, no_resize=True, no_collapse=True):
    dpg.add_text("Config.yaml:")
    dpg.add_input_text(tag="##configtext", multiline=True, readonly=True, width=380, height=220)
    dpg.add_button(label="Close", callback=hide_config)

with dpg.window(label="About Window", tag="About Window", width=350, height=200, show=False, no_resize=True, no_collapse=True):
    dpg.add_text("BarkEngine25 - Debug/Control Panel")
    dpg.add_text("Made by FunnyTom777")
    dpg.add_text("DearPyGui Edition")
    dpg.add_text("Project Home: github.com/FunnyTom777/BarkEngine25")
    dpg.add_button(label="Close", callback=hide_about)

dpg.create_viewport(title="BarkEngine25 Control Panel", width=650, height=550)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
