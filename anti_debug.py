import sys
import os
import platform
import traceback

class AntiDebugger:
    def __init__(self):
        self.debug_detected = False
        self.check_count = 0
        self.last_check_time = time.time()

    def is_debugger_present(self):
        """Check for common debugging indicators"""
        self.check_count += 1
        current_time = time.time()
        
        # Only perform checks every second to avoid performance impact
        if current_time - self.last_check_time < 1:
            return self.debug_detected
            
        self.last_check_time = current_time

        # Check for common debugging environmental variables
        debug_env_vars = ['PYTHONDEVMODE', 'PYTHONDEBUG', 'PYTHONINSPECT']
        for var in debug_env_vars:
            if var in os.environ:
                self.debug_detected = True
                return True

        # Check for trace function
        if sys.gettrace() is not None:
            self.debug_detected = True
            return True

        # Check for suspicious module imports
        suspicious_modules = ['pdb', 'pydevd', 'ide_debug']
        for module in sys.modules:
            if any(sus in module.lower() for sus in suspicious_modules):
                self.debug_detected = True
                return True

        return False

    def get_check_count(self):
        return self.check_count