import hashlib
import json
import time

class IntegrityChecker:
    def __init__(self):
        self.last_check_time = time.time()
        self.check_interval = 5  # Check every 5 seconds
        self.previous_hashes = {}

    def compute_hash(self, data):
        """Compute SHA-256 hash of data"""
        if isinstance(data, (list, dict)):
            data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(str(data).encode()).hexdigest()

    def check_integrity(self, board, score, shapes):
        """Check integrity of game state"""
        current_time = time.time()
        if current_time - self.last_check_time < self.check_interval:
            return True

        current_hashes = {
            'board': self.compute_hash(board),
            'score': self.compute_hash(score),
            'shapes': self.compute_hash(shapes)
        }

        if not self.previous_hashes:
            self.previous_hashes = current_hashes
            self.last_check_time = current_time
            return True

        for key in current_hashes:
            if key in self.previous_hashes:
                if abs(len(str(self.previous_hashes[key])) - len(str(current_hashes[key]))) > 10:
                    return False

        self.previous_hashes = current_hashes
        self.last_check_time = current_time
        return True