### Functions you can call from Dependancies.py:
---
**loadmods**
The Load mods function loads all **.bemod** files from the /mods directory, and then lists them in the manifest.yaml (located in the /mods directory).

Example:
```
import dependencies

dependencies.loadmods()
```

OR alterntivly, you can call:
```
import dependencies

dependencies.loadmods("disable")
```
To disable Mod Loading (Bassically just dosent write anything to the manifest.yaml)

---
**error**
The error function does.. well.. errors!
you can do:

```
import dependencies

dependencies.error(1)
```

Will do a "Mod Problem Error", and you can also do:

```
import dependencies

dependencies.error(2)
```

to do a "Problem Injecting Mods" error!

here is the total list of errors you can call:

```
1 – Mod problem
2 – Problem injecting mods into Motor Town
```

---



### For the Memory Editor Module:
The public API (class MemoryEditor)
Method	Purpose	Example
__init__(config_path)	Read the YAML file and keep the data in memory.	mem = MemoryEditor('config.yaml')
open_process()	Locate the target game by its executable name and open it with full access.	mem.open_process()
close()	Close the handle returned by OpenProcess.	mem.close()
resolve_pointer(name)	Internal: follow the offset chain described in the config and return the final address.	addr = mem.resolve_pointer('health')
read_bytes(address, size)	Low‑level wrapper for ReadProcessMemory.	b = mem.read_bytes(0x12345678, 4)
write_bytes(address, data)	Low‑level wrapper for WriteProcessMemory.	mem.write_bytes(0x12345678, b'\x01\x00\x00\x00')
Convenience readers/writers	Convert raw bytes into Python numbers.	mem.read_int(0x12345678)
get_value(name, fmt='i')	Resolve a named pointer and read a value using a struct format.	hp = mem.get_value('health')
set_value(name, value, fmt='i')	Resolve a named pointer and write a value using a struct format.	mem.set_value('ammo', 999, fmt='h')
Format strings (fmt)
The fmt parameter is any struct format string:

Value	Description	Size
'i'	32‑bit signed integer (int)	4
'I'	32‑bit unsigned integer	4
'f'	32‑bit IEEE‑754 floating point	4
'h'	16‑bit signed short	2
'H'	16‑bit unsigned short	2
'b'	8‑bit signed byte	1
'B'	8‑bit unsigned byte	1
Note: get_value/set_value automatically compute the size from the format (struct.calcsize(fmt)).

4. Example script (example.py)
from memory_editor import MemoryEditor

def main():
    mem = MemoryEditor('config.yaml')
    mem.open_process()

    try:
        # Read current health
        hp = mem.get_value('health')
        print(f"Health: {hp}")

        # Force health to 999
        mem.set_value('health', 999)
        print("Health set to 999")

        # Read ammo stored as a short
        ammo = mem.get_value('ammo', fmt='h')
        print(f"Ammo: {ammo}")

        # Set speed (float) to 9999.99
        mem.set_value('speed', 9999.99, fmt='f')
        print("Speed set to 9999.99")

    finally:
        mem.close()

if __name__ == "__main__":
    main()