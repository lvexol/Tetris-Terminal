import time
from collections import deque

class InputValidator:
    def __init__(self, max_queue_size=10):
        self.key_press_times = deque(maxlen=max_queue_size)
        self.min_interval = 0.05  # Minimum allowed time between keypresses (50ms)
        self.suspicious_count = 0
        self.max_suspicious = 5

    def validate_input(self, key):
        """Validate timing of key inputs"""
        current_time = time.time()
        
        if self.key_press_times:
            interval = current_time - self.key_press_times[-1]
            if interval < self.min_interval:
                self.suspicious_count += 1
            else:
                self.suspicious_count = max(0, self.suspicious_count - 1)

        self.key_press_times.append(current_time)
        
        # Check for suspicious patterns
        if self.suspicious_count >= self.max_suspicious:
            return False
        
        return True

    def reset(self):
        """Reset the validator state"""
        self.key_press_times.clear()
        self.suspicious_count = 0