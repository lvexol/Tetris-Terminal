import ctypes
import os
import mmap
from ctypes import wintypes

class MemoryUtils:
    def __init__(self):
        """Initialize MemoryUtils with an empty list of addresses."""
        self.cached_addresses = []

    def cache_address(self, address):
        """Add a memory address to the list of cached addresses for monitoring."""
        self.cached_addresses.append(address)

    def is_memory_readable(self, address, size):
        """
        Check if the specified memory region is readable.
        
        :param address: Starting address of the memory region.
        :param size: Size of the memory region in bytes.
        :return: True if the region is readable, False otherwise.
        """
        try:
            # Try to read the specified memory region
            ctypes.string_at(address, size)
            return True
        except (OSError, ValueError, ctypes.ArgumentError):
            return False

    def scan_memory_region(self, address, size):
        """
        Scan a memory region to check for unexpected modifications.
        
        :param address: Starting address of the memory region.
        :param size: Size of the memory region in bytes.
        :return: True if no modifications are detected, False if modified.
        """
        original_content = ctypes.string_at(address, size)  # Initial snapshot of memory region
        
        # Re-read the memory region and compare with the original content
        try:
            current_content = ctypes.string_at(address, size)
            return current_content == original_content
        except (OSError, ValueError, ctypes.ArgumentError):
            return False

    def protect_memory_region(self, address, size, protection):
        """
        Set memory protection on a specific region.
        
        :param address: Starting address of the memory region.
        :param size: Size of the memory region in bytes.
        :param protection: Protection flags (e.g., read-only, read-write).
        :return: True if protection set successfully, False otherwise.
        """
        if os.name == 'nt':
            return self._set_protection_windows(address, size, protection)
        elif os.name == 'posix':
            return self._set_protection_posix(address, size, protection)
        return False

    def _set_protection_windows(self, address, size, protection):
        """Set memory protection on Windows."""
        PAGE_READONLY = 0x02
        PAGE_READWRITE = 0x04

        protection_map = {
            'read-only': PAGE_READONLY,
            'read-write': PAGE_READWRITE
        }
        protection_flag = protection_map.get(protection, PAGE_READONLY)

        kernel32 = ctypes.WinDLL('kernel32')
        old_protect = wintypes.DWORD()

        result = kernel32.VirtualProtect(
            ctypes.c_void_p(address), 
            ctypes.c_size_t(size), 
            protection_flag, 
            ctypes.byref(old_protect)
        )

        return bool(result)

    def _set_protection_posix(self, address, size, protection):
        """Set memory protection on POSIX systems."""
        prot_flags = mmap.PROT_READ if protection == 'read-only' else mmap.PROT_READ | mmap.PROT_WRITE

        # Align address to page boundary
        page_size = mmap.PAGESIZE
        aligned_address = address - (address % page_size)

        try:
            # Apply protection
            mmap.mmap(-1, size, prot=prot_flags, offset=aligned_address)
            return True
        except (OSError, ValueError):
            return False

    def detect_protection_change(self, address, size):
        """
        Detect if the protection level of a memory region has changed.
        
        :param address: Starting address of the memory region.
        :param size: Size of the memory region in bytes.
        :return: True if protection change detected, False otherwise.
        """
        # Placeholder implementation for detecting memory protection changes.
        # This typically requires platform-specific monitoring.
        return False

