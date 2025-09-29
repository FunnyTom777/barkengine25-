import yaml # type: ignore
from pathlib import Path

# Path to the manifest file (shared with barkengine25)
MANIFEST_FILE = Path("manifest.yaml")


def _load_manifest():
    """Load the YAML manifest file as a dict (or create a new one)."""
    if MANIFEST_FILE.exists():
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {"mods": []}


def _save_manifest(data):
    """Write the manifest dict back to the YAML file."""
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False)


def registermod(modxml: str, modid: str, modname: str, modauthor: str):
    data = _load_manifest()

    if "mods" not in data:
        data["mods"] = []
    if "files" not in data:
        data["files"] = []

    # Avoid duplicate IDs
    for mod in data["mods"]:
        if mod["id"] == modid:
            raise ValueError(f"Mod with id '{modid}' already registered!")

    # Add XML file to "files" list if not already there
    if modxml not in data["files"]:
        data["files"].append(modxml)

    data["mods"].append({
        "id": modid,
        "name": modname,
        "author": modauthor,
        "xml": modxml,
        "priority": None
    })

    _save_manifest(data)
    print(f"[UraniumAPI] Registered mod: {modname} (id={modid})")


def listregisteredmods():
    """
    List all registered mods from manifest.yaml.
    """
    data = _load_manifest()
    return data.get("mods", [])


def allocatemodpriorities():
    """
    Allocate mod priorities in order of registration.
    First registered = lowest priority, last registered = highest.
    """
    data = _load_manifest()

    for i, mod in enumerate(data.get("mods", []), start=1):
        mod["priority"] = i

    _save_manifest(data)
    print("[UraniumAPI] Mod priorities allocated successfully.")
