import dependencies
import os
from modstuff import load_mods_from_folder
from rich import print
import subprocess

# Decide whether to disable mod loading
if dependencies.CONFIG.get("disablemodload"):
    dependencies.loadmods("disable")
else:
    dependencies.loadmods()

import sys
import time

def loading_bar(total_steps, bar_length=50, prefix='Loading: ', suffix='Done', delay=0.05):
    """
    total_steps:   how many steps the task will have
    bar_length:    width of the bar in characters
    prefix:        text printed before the bar
    suffix:        text printed after the bar
    delay:         artificial delay (seconds) – remove in real code
    """
    for step in range(1, total_steps + 1):
        # ---- build the bar ----
        percent = 100 * step / total_steps
        filled_len = int(bar_length * step // total_steps)
        bar = '#' * filled_len + '-' * (bar_length - filled_len)

        # ---- write it to stdout, keep the cursor on the same line ----
        sys.stdout.write(f'\r{prefix}[{bar}] {percent:6.2f}% {suffix}')
        sys.stdout.flush()

        # ---- do the real work (here we just sleep) ----
        time.sleep(delay)

    # Finish with a newline so subsequent output starts on a fresh line
    sys.stdout.write('\n')



def registermods() -> None:
    mods = load_mods_from_folder()      # <-- the helper above

    # Example: register every valid mod with your engine‑API
    for mod in mods:
        # your custom logic – e.g. add to a registry, instantiate objects, etc.
        print(f"[green]Registering {mod['modId']} – {mod['name']}[/green]")

print(" ")
registermods()
print(" ")
print("[red]Loading BarkEngine...[red]")
loading_bar(120, delay=0.05)
print("[green]Loading Complete![green]")
print(" ")
makenewuser = input("Create new user? (y/n): ")
if makenewuser.lower() == "y":
    newusername = input("Enter new username: ")
    newpassword = input("Enter new password: ")
    dependencies.createuser(newusername, newpassword)
    