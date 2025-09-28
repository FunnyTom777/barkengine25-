from rich import print # type: ignore
import os
import time
from pathlib import Path
from typing import Optional





current_dir = os.path.dirname(os.path.abspath(__file__))
mods_path   = os.path.join(current_dir, "Mods")




# V-------Define Funtions---------V
import os
import time
import os
import time

def loadmods(action: str | None = None) -> None:
    """
    Write the list of .xml files into Mods/Manifest.yaml.

    Parameters
    ----------
    action : str | None
        If set to "disable" (case‑insensitive) the manifest will be
        written with an empty file list.  Any other value (or None) will
        cause the function to scan the mods directory and list all
        discovered .xml files.

    Notes
    -----
    * The function always overwrites Mods/Manifest.yaml – no old
      entries survive unless they are re‑written by a subsequent call.
    * The returned file will contain a minimal YAML fragment:
      ``files:\n  - <mod1>.xml\n  - <mod2>.xml``  (or just ``files:`` if
      disabled).
    """
    # 1️⃣  Absolute path to the sibling “mods” folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mods_path  = os.path.join(script_dir, "mods")

    # 2️⃣  Decide what to list based on the action argument
    if action and action.lower() == "disable":
        disablemodload = 1
        xml_files = []                     # nothing to list
    else:
        disablemodload = 0
        xml_files = [
            name for name in os.listdir(mods_path)
            if name.lower().endswith(".xml") and
               os.path.isfile(os.path.join(mods_path, name))
        ]

    # 3️⃣  Write the manifest (always overwriting the old file)
    manifest_path = os.path.join(mods_path, "Manifest.yaml")
    with open(manifest_path, "w", encoding="utf-8") as out:
        out.write("files:\n")
        for fname in xml_files:
            out.write(f"  - {fname}\n")

    # Optional – give the user a quick summary
    print("[red]Loading Mods...[red]")
    time.sleep(2)
    if disablemodload == 0:
        print(f"{len(xml_files)} .xml file(s) written to [green]Mods/Manifest.yaml[green]")
    else:
        print(f"{len(xml_files)} .xml file(s) written to [green]Mods/Manifest.yaml[green] "
              "[red](Mod Loading Disabled in config.yaml!)[red]")


# Define Error handaling:

def error(error_code: int) -> None:
    """
    Display a helpful error message for the given error code.

    Parameters
    ----------
    error_code : int
        1 – Mod problem
        2 – Problem injecting mods into Motor Town
    """
    if error_code == 1:
        print("[red]ERROR: Problem with a Mod (Try uninstalling some mods!)[red]")

    elif error_code == 2:
        print("[red]ERROR: Problem injecting mods into Motor Town![red]")
        # Ask the user if they want more details
        more_details = input("Press 1 for more info, 0 to cancel: ").strip()
        # Handle bad input safely
        try:
            more_details_int = int(more_details)
        except ValueError:
            more_details_int = 0

        if more_details_int == 1:
            print(
                "This could be due to a mismatch in version between BarkEngine "
                "and your Motor Town version, a Motor Town patch that changed "
                "address values, or some unknown external factor(s)."
            )

    else:
        print(f"Unknown error code: {error_code}")


CONFIG_FILE = "config.yaml"

def _parse_config(path: str) -> dict:
    """
    Very small “YAML” parser that understands lines like:
        key = value
    or
        key: value

    Returns a dictionary of the parsed values.
    """
    config: dict = {}

    if not os.path.exists(path):
        # No config file – fall back to an empty dict
        return config

    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue  # skip blanks and comments

            # Prefer '=' but fall back to ':' if needed
            if "=" in line:
                key, value = map(str.strip, line.split("=", 1))
            elif ":" in line:
                key, value = map(str.strip, line.split(":", 1))
            else:
                # line is not in the expected format – ignore it
                continue

            # Normalise booleans (`true/false`) to Python bool
            if value.lower() == "true":
                config[key] = True
            elif value.lower() == "false":
                config[key] = False
            else:
                config[key] = value

    return config


# Publicly expose the configuration once, at import time
CONFIG = _parse_config(CONFIG_FILE)

def createuser(username: str, password: str) -> None:
    """
    Create a new user by appending to users.txt.

    encode the password using sha Hashing and then store it in users.txt

    Parameters
    ----------
    username : str
        The username for the new user.
    password : str
        The password for the new user.
    """
    users_file = "users.txt"
    import hashlib
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    with open(users_file, "a", encoding="utf-8") as f:
        f.write(f"{username}:{hashed_password}\n")
    activeuser = username  # Set the active user
    print(f"[green]User '{username}' created successfully.[/green]")

def authenticateuser(username: str, password: str) -> bool:
    """
    Authenticate a user by checking users.txt.

    Parameters
    ----------
    username : str
        The username to authenticate.
    password : str
        The password to authenticate.

    Returns
    -------
    bool
        True if authentication is successful, False otherwise.
    """
    users_file = "users.txt"
    import hashlib
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if not os.path.exists(users_file):
        print("[red]No users found. Please create a user first.[/red]")
        return False

    with open(users_file, "r", encoding="utf-8") as f:
        for line in f:
            stored_username, stored_hashed_password = line.strip().split(":", 1)
            if stored_username == username and stored_hashed_password == hashed_password:
                activeuser = username  # Set the active user
                return True

    print("[red]Authentication failed. Invalid username or password.[/red]")
    return False