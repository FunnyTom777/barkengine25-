#!/usr/bin/env python3
"""
mod_loader.py
~~~~~~~~~~~~~

Utility that loads all mod XML files from `Mods/` and returns
a list of dictionaries describing each mod.
"""

from __future__ import annotations

import logging
import pathlib
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from rich import print

# --------------------------------------------------------------------------- #
#  Configuration
# --------------------------------------------------------------------------- #

MODS_DIR = pathlib.Path("Mods")          # relative to this script's directory
# If you already have a file list somewhere, pass it to load_mods_from_files()
# example: existing_file_list = ["mod1.xml", "mod2.xml"]

# --------------------------------------------------------------------------- #
#  Logging
# --------------------------------------------------------------------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)

# --------------------------------------------------------------------------- #
#  Helper: Safely extract text from an element
# --------------------------------------------------------------------------- #

def _elem_text(root: ET.Element, tag: str, *,
               required: bool = False,
               default: Optional[str] = None) -> Optional[str]:
    """
    Return the text of the first child matching *tag*.

    *required* – if True and the tag is missing, a warning is logged.
    *default*  – value returned when the tag is missing.
    """
    elem = root.find(tag)
    if elem is None:
        if required:
            logging.warning("Missing required tag <%s> in %s", tag, root.tag)
        return default
    return elem.text.strip() if elem.text else None


# --------------------------------------------------------------------------- #
#  Helper: Parse a mod's <engine> block into a dict
# --------------------------------------------------------------------------- #

def _parse_engine(root: ET.Element) -> Optional[Dict]:
    engine_elem = root.find("engine")
    if engine_elem is None:
        logging.warning("Missing <engine> section in %s", root.tag)
        return None

    def _num(tag: str, *, required: bool = False) -> Optional[float]:
        txt = _elem_text(engine_elem, tag, required=required)
        if txt is None:
            return None
        try:
            return float(txt)
        except ValueError:
            logging.warning("Invalid number for <%s>: %s", tag, txt)
            return None

    engine = {
        "hp": _num("hp", required=True),
        "torque": _num("torque"),
        "weight": _num("weight"),
        "fuelType": _elem_text(engine_elem, "fuelType"),
        "fuelEfficiency": _num("fuelEfficiency"),
        "turbo": _elem_text(engine_elem, "turbo"),
        "turboBoost": _num("turboBoost"),
        # powerCurve: list of dicts with rpm and multiplier
        "powerCurve": [],
    }

    # Optional power curve points
    for point in engine_elem.findall("powerCurve/point"):
        try:
            rpm = int(point.attrib.get("rpm", 0))
            mult = float(point.attrib.get("multiplier", 1.0))
            engine["powerCurve"].append({"rpm": rpm, "multiplier": mult})
        except (ValueError, TypeError):
            logging.warning("Malformed <point> in powerCurve of %s", root.tag)

    return engine


# --------------------------------------------------------------------------- #
#  Main loader function
# --------------------------------------------------------------------------- #

def load_mods_from_folder(folder: pathlib.Path = MODS_DIR) -> List[Dict]:
    """
    Scan *folder* for *.xml files, parse them and return a list of mod dicts.

    Skips files that cannot be parsed or that are missing a <mod> root tag.
    """
    mods: List[Dict] = []

    if not folder.is_dir():
        logging.error("Mods folder %s does not exist.", folder)
        return mods

    xml_files = sorted(folder.rglob("*.xml"))
    if not xml_files:
        logging.info("No XML mod files found in %s.", folder)
        return mods

    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except ET.ParseError as exc:
            logging.error("Failed to parse %s: %s", xml_file.name, exc)
            continue

        if root.tag != "mod":
            logging.warning("File %s does not contain <mod> root; skipping.", xml_file.name)
            continue

        # ------------------------------------------------------------------- #
        #  Parse each logical block
        # ------------------------------------------------------------------- #
        mod_dict: Dict = {}

        # Basic identification (required)
        mod_dict["modId"] = _elem_text(root, "modInfo/modId", required=True)
        mod_dict["name"]   = _elem_text(root, "modInfo/name", required=True)
        mod_dict["author"] = _elem_text(root, "modInfo/author")
        mod_dict["version"]= _elem_text(root, "modInfo/version")
        mod_dict["description"] = _elem_text(root, "modInfo/description")
        mod_dict["license"] = _elem_text(root, "modInfo/license")
        mod_dict["modPage"] = _elem_text(root, "modInfo/modPage")

        # Compatibility (optional)
        comp_root = root.find("compatibility")
        if comp_root is not None:
            mod_dict["compatibility"] = {
                "minEngine": _elem_text(comp_root, "minEngine"),
                "maxEngine": _elem_text(comp_root, "maxEngine"),
                "dependencies": [dep.text for dep in comp_root.findall("dependencies/dependency") if dep.text],
            }

        # Assets (optional)
        assets_root = root.find("assets")
        if assets_root is not None:
            mod_dict["assets"] = {
                "icon": _elem_text(assets_root, "icon"),
                "textures": [tex.text for tex in assets_root.findall("textures/texture") if tex.text],
                "sounds": [snd.text for snd in assets_root.findall("sounds/sound") if snd.text],
            }

        # Engine
        engine = _parse_engine(root)
        if engine is not None:
            mod_dict["engine"] = engine

        # Vehicle (optional)
        vehicle_root = root.find("vehicle")
        if vehicle_root is not None:
            mod_dict["vehicle"] = {
                "weightMultiplier": _elem_text(vehicle_root, "weightMultiplier"),
                "soundPitch": _elem_text(vehicle_root, "soundPitch"),
            }

        # Mod Options
        opt_root = root.find("modOptions")
        if opt_root is not None:
            mod_dict["modOptions"] = {
                "enableUI": _elem_text(opt_root, "enableUI"),
                "uiTheme": _elem_text(opt_root, "uiTheme"),
                "keyBindings": _elem_text(opt_root, "keyBindings"),
                "localization": _elem_text(opt_root, "localization"),
            }

        # Custom data – just drop the raw XML subtree for flexibility
        custom_root = root.find("customData")
        if custom_root is not None:
            mod_dict["customData"] = ET.tostring(custom_root, encoding="unicode")

        mods.append(mod_dict)

    logging.info("Loaded %d mod(s) from %s.", len(mods), folder)
    return mods


# --------------------------------------------------------------------------- #
#  Convenience wrapper: use an externally supplied file list
# --------------------------------------------------------------------------- #

def load_mods_from_files(file_list: List[str], folder: pathlib.Path = MODS_DIR) -> List[Dict]:
    """
    Same as :func:`load_mods_from_folder` but takes a pre‑computed list of
    filenames (e.g. read from a config or a database).

    *file_list* is a list of filenames (without paths); each file is resolved
    relative to *folder*.
    """
    mods: List[Dict] = []

    for fn in file_list:
        xml_file = folder / fn
        if not xml_file.exists():
            logging.warning("File %s listed but does not exist.", fn)
            continue
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
        except ET.ParseError as exc:
            logging.error("Failed to parse %s: %s", fn, exc)
            continue
        if root.tag != "mod":
            logging.warning("File %s does not contain <mod> root; skipping.", fn)
            continue

        mods.append(_parse_mod_tree(root, xml_file.name)) # type: ignore

    logging.info("Loaded %d mod(s) from file list.", len(mods))
    return mods


# --------------------------------------------------------------------------- #
#  Demo usage (only runs when executed as a script)
# --------------------------------------------------------------------------- #

if __name__ == "__main__":          # pragma: no cover
    mods = load_mods_from_folder()
    for m in mods:
        print(f"• {m['modId']} – {m['name']} (v{m.get('version')}) by {m.get('author', '???')}")
