import yaml # type: ignore
import os

def sup():
    return "sup"
currentmoney = 0

def addmoney(money):
    global currentmoney
    currentmoney += money
    return currentmoney

def takemoney(money):
    global currentmoney
    currentmoney -= money
    return currentmoney


# --- load config.yaml first ---
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

SAVE_FILE = config.get("SAVE_FILE", "savegame.yaml")  # fallback if missing

def savegame(currentmoney):
    # if file already exists, load it
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    # update only the money value
    data["currentmoney"] = currentmoney

    # write back to file
    with open(SAVE_FILE, "w") as f:
        yaml.dump(data, f)

def loadgame():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    return {}

    # update only the money value
    data["currentmoney"] = currentmoney

    # write back to file
def loadgame():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = yaml.safe_load(f) or {}
            global currentmoney
            currentmoney = data.get("currentmoney", 0)
            return data
    return {}

def handle_chat_message(message):
    """Handle regular chat messages (non-commands)"""
    # You can add any chat processing logic here
    # For now, we'll just echo back the message
