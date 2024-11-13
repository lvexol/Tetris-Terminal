import ctypes
import os
import tempfile
from memory_protection.process_monitor import ProcessMonitor
from memory_protection.integrity_checker import IntegrityChecker
from memory_protection.memory_utils import MemoryUtils

def test_process_monitor():
    print("Testing ProcessMonitor...")

    # Initialize ProcessMonitor and set up a monitoring address
    process_monitor = ProcessMonitor()
    test_address = 0x1234
    process_monitor.monitor_address(test_address)

    # Check if the address is now being monitored
    assert test_address in process_monitor.monitored_addresses
    print("ProcessMonitor test passed.")

def test_integrity_checker():
    print("Testing IntegrityChecker...")

    # Create a temporary file to represent the executable
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(b"Sample data for integrity test.")
    
    try:
        # Initialize IntegrityChecker and calculate hash
        integrity_checker = IntegrityChecker()
        initial_hash = integrity_checker.calculate_hash(temp_file_path)

        # Simulate a file integrity check
        assert integrity_checker.verify_file_integrity(temp_file_path, initial_hash)
        print("Initial integrity check passed.")

        # Modify the file and verify integrity check fails
        with open(temp_file_path, "a") as file:
            file.write("Additional data to change hash.")

        assert not integrity_checker.verify_file_integrity(temp_file_path, initial_hash)
        print("Modified integrity check passed.")
    finally:
        os.remove(temp_file_path)

def test_memory_utils():
    print("Testing MemoryUtils...")

    # Initialize MemoryUtils
    memory_utils = MemoryUtils()
    test_address = ctypes.addressof(ctypes.create_string_buffer(b"Test data"))
    memory_utils.cache_address(test_address)

    # Check if the address is cached
    assert test_address in memory_utils.cached_addresses
    print("Memory address caching test passed.")

    # Check if memory is readable
    assert memory_utils.is_memory_readable(test_address, 9)
    print("Memory readability test passed.")

    # Check scan for modifications (no modification expected initially)
    assert memory_utils.scan_memory_region(test_address, 9)
    print("Memory scan test passed (no modifications detected).")

    # Simulate modification
    ctypes.memmove(test_address, b"Modified", 8)
    assert not memory_utils.scan_memory_region(test_address, 9)
    print("Memory scan test passed (modification detected).")

    # Protect memory region (POSIX only demonstration; may require elevated permissions on some systems)
    protection_result = memory_utils.protect_memory_region(test_address, 9, 'read-only')
    print("Memory protection test result (platform-dependent):", protection_result)

def run_tests():
    print("Running tests...")
    test_process_monitor()
    test_integrity_checker()
    test_memory_utils()
    print("All tests completed.")

if __name__ == "__main__":
    run_tests()
