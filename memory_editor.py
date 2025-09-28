# memory_editor.py
"""
A tiny, Windows‑only memory editing helper for games (e.g. Motor Town Behind the Wheel).

Usage
-----
>>> from memory_editor import MemoryEditor
>>> mem = MemoryEditor('config.yaml')
>>> mem.open_process()              # finds the target process
>>> addr = mem.get_address('health') # resolves the pointer chain
>>> old = mem.read_int(addr)
>>> mem.write_int(addr, 999)         # set health to 999
"""

import ctypes
import struct
import psutil
import yaml
import os
import sys
from ctypes import wintypes

# ────────────────────────────────────────────────────────────────
# Windows API wrappers
# ────────────────────────────────────────────────────────────────
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
OpenProcess.restype = wintypes.HANDLE

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [wintypes.HANDLE,
                              wintypes.LPCVOID,
                              wintypes.LPVOID,
                              ctypes.c_size_t,
                              ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = wintypes.BOOL

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [wintypes.HANDLE,
                               wintypes.LPVOID,
                               wintypes.LPCVOID,
                               ctypes.c_size_t,
                               ctypes.POINTER(ctypes.c_size_t)]
WriteProcessMemory.restype = wintypes.BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

# ────────────────────────────────────────────────────────────────
# Helper utilities
# ────────────────────────────────────────────────────────────────
class MemoryEditor:
    # Windows access rights
    PROCESS_ALL_ACCESS = 0x001F0FFF

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.proc_name = self.config['application']['name']
        self.pid = None
        self.handle = None

    # ----------------------------------------------------------------
    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r') as f:
            cfg = yaml.safe_load(f)
        if 'application' not in cfg or 'name' not in cfg['application']:
            raise ValueError("config.yaml must contain 'application: name:'")
        return cfg

    # ----------------------------------------------------------------
    def open_process(self):
        """Find the process by name (first instance) and open it with full access."""
        if self.handle:
            return  # already open

        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == self.proc_name:
                self.pid = proc.info['pid']
                break
        else:
            raise RuntimeError(f"Could not find process '{self.proc_name}'")

        self.handle = OpenProcess(self.PROCESS_ALL_ACCESS, False, self.pid)
        if not self.handle:
            err = ctypes.get_last_error()
            raise OSError(f"OpenProcess failed with error {err}")

    # ----------------------------------------------------------------
    def close(self):
        if self.handle:
            CloseHandle(self.handle)
            self.handle = None

    # ----------------------------------------------------------------
    def _get_module_base(self, module_name: str) -> int:
        """Return the base address of a module inside the target process."""
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'open_files']):
            if proc.info['pid'] != self.pid:
                continue
            try:
                for m in proc.memory_maps():
                    if os.path.basename(m.path).lower() == module_name.lower():
                        return int(m.addr.split('-')[0], 16)
            except Exception:
                continue
        raise RuntimeError(f"Module '{module_name}' not found in process {self.proc_name}")

    # ----------------------------------------------------------------
    def resolve_pointer(self, name: str) -> int:
        """
        Resolve a pointer chain defined under `pointers: <name>` in config.yaml.
        Returns the final absolute address.
        """
        if name not in self.config.get('pointers', {}):
            raise KeyError(f"No pointer named '{name}' in config")
        info = self.config['pointers'][name]
        module = info['module']
        offsets = info['offsets']

        # Start at module base + first offset
        addr = self._get_module_base(module) + offsets[0]

        # For all subsequent offsets, dereference pointer and add offset
        for off in offsets[1:]:
            ptr_bytes = self.read_bytes(addr, ctypes.sizeof(ctypes.c_void_p))
            ptr = struct.unpack('<Q' if sys.maxsize > 2**32 else '<I', ptr_bytes)[0]
            addr = ptr + off

        return addr

    # ----------------------------------------------------------------
    def read_bytes(self, address: int, size: int) -> bytes:
        """Read raw bytes from target process."""
        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t()
        if not ReadProcessMemory(self.handle, ctypes.c_void_p(address), buffer, size, ctypes.byref(bytes_read)):
            err = ctypes.get_last_error()
            raise OSError(f"ReadProcessMemory failed at {hex(address)} (error {err})")
        return buffer.raw

    def write_bytes(self, address: int, data: bytes):
        """Write raw bytes to target process."""
        size = len(data)
        c_data = ctypes.create_string_buffer(data)
        bytes_written = ctypes.c_size_t()
        if not WriteProcessMemory(self.handle, ctypes.c_void_p(address), c_data, size, ctypes.byref(bytes_written)):
            err = ctypes.get_last_error()
            raise OSError(f"WriteProcessMemory failed at {hex(address)} (error {err})")

    # ----------------------------------------------------------------
    # Convenience helpers for common types
    # ----------------------------------------------------------------
    def read_int(self, address: int) -> int:
        return struct.unpack('<i', self.read_bytes(address, 4))[0]

    def write_int(self, address: int, value: int):
        self.write_bytes(address, struct.pack('<i', value))

    def read_float(self, address: int) -> float:
        return struct.unpack('<f', self.read_bytes(address, 4))[0]

    def write_float(self, address: int, value: float):
        self.write_bytes(address, struct.pack('<f', value))

    def read_short(self, address: int) -> int:
        return struct.unpack('<h', self.read_bytes(address, 2))[0]

    def write_short(self, address: int, value: int):
        self.write_bytes(address, struct.pack('<h', value))

    def read_byte(self, address: int) -> int:
        return struct.unpack('B', self.read_bytes(address, 1))[0]

    def write_byte(self, address: int, value: int):
        self.write_bytes(address, struct.pack('B', value))

    # ----------------------------------------------------------------
    # High‑level convenience: get the value of a named pointer
    # ----------------------------------------------------------------
    def get_value(self, name: str, fmt: str = 'i') -> int:
        """
        Resolve the pointer named `name` and read a value from it.
        fmt can be any struct format string (default 'i' – 32‑bit int).
        """
        addr = self.resolve_pointer(name)
        return struct.unpack(fmt, self.read_bytes(addr, struct.calcsize(fmt)))[0]

    def set_value(self, name: str, value, fmt: str = 'i'):
        """
        Resolve the pointer named `name` and write a value to it.
        fmt can be any struct format string (default 'i' – 32‑bit int).
        """
        addr = self.resolve_pointer(name)
        self.write_bytes(addr, struct.pack(fmt, value))
