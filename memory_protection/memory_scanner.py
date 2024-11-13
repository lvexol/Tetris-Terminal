# memory_protection/memory_scanner.py
import os
import sys
import time
import json
import random
import hashlib
import struct
import psutil
import ctypes
from threading import Thread, Lock
from collections import defaultdict
from datetime import datetime

class MemorySnapshot:
    def __init__(self):
        self.snapshot_data = {}
        self.snapshot_time = None
        self.hash_cache = {}
        self.memory_lock = Lock()
        self.validation_count = 0
        self.last_validation = time.time()
        self.suspicious_activities = defaultdict(int)
        
    def _generate_memory_fingerprint(self, data):
        """Generate a unique fingerprint for memory data"""
        if isinstance(data, (list, dict)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
            
        # Create a complex hash using multiple algorithms
        sha256_hash = hashlib.sha256(data_str.encode()).hexdigest()
        md5_hash = hashlib.md5(data_str.encode()).hexdigest()
        
        # Combine hashes with additional entropy
        timestamp = str(time.time()).encode()
        combined = hashlib.sha512(sha256_hash.encode() + md5_hash.encode() + timestamp).hexdigest()
        
        return combined[:64]  # Return first 64 chars for consistency

    def _serialize_game_state(self, game_state):
        """Serialize game state with additional metadata"""
        serialized = {
            'timestamp': datetime.now().isoformat(),
            'process_id': os.getpid(),
            'state_data': game_state,
            'memory_addresses': {
                key: id(value) for key, value in game_state.items()
            },
            'validation_count': self.validation_count
        }
        return serialized

    def create_snapshot(self, game_state):
        """Create a comprehensive memory snapshot"""
        with self.memory_lock:
            try:
                serialized_state = self._serialize_game_state(game_state)
                self.snapshot_data = {
                    'state': serialized_state,
                    'fingerprint': self._generate_memory_fingerprint(serialized_state),
                    'timestamp': time.time(),
                    'process_info': {
                        'cpu_percent': psutil.Process().cpu_percent(),
                        'memory_info': dict(psutil.Process().memory_info()._asdict()),
                        'num_threads': psutil.Process().num_threads()
                    }
                }
                self.snapshot_time = time.time()
                self.hash_cache.clear()  # Clear previous cache
                return True
            except Exception as e:
                self._log_security_event(f"Snapshot creation failed: {str(e)}")
                return False

    def _validate_memory_addresses(self, current_state):
        """Validate memory addresses haven't been tampered with"""
        original_addresses = self.snapshot_data['state']['memory_addresses']
        current_addresses = {key: id(value) for key, value in current_state.items()}
        
        for key in original_addresses:
            if key in current_addresses:
                # Check if memory address has changed unexpectedly
                if abs(current_addresses[key] - original_addresses[key]) > 1000000:
                    self._log_security_event(f"Suspicious memory address change detected for {key}")
                    return False
        return True

    def _check_process_integrity(self):
        """Verify process integrity and environment"""
        current_process = psutil.Process()
        
        # Check for suspicious changes in process characteristics
        if abs(current_process.cpu_percent() - 
               self.snapshot_data['process_info']['cpu_percent']) > 50:
            self._log_security_event("Suspicious CPU usage detected")
            return False
            
        current_memory = dict(current_process.memory_info()._asdict())
        original_memory = self.snapshot_data['process_info']['memory_info']
        
        # Check for unusual memory changes
        for key in original_memory:
            if key in current_memory:
                if abs(current_memory[key] - original_memory[key]) > 10000000:  # 10MB threshold
                    self._log_security_event(f"Suspicious memory change detected: {key}")
                    return False
                    
        return True

    def validate_state(self, current_state):
        """Comprehensive state validation"""
        with self.memory_lock:
            try:
                self.validation_count += 1
                current_time = time.time()
                
                # Rate limiting for validation checks
                if current_time - self.last_validation < 0.1:  # 100ms minimum between checks
                    return True
                    
                self.last_validation = current_time

                # Basic snapshot existence check
                if not self.snapshot_data:
                    self._log_security_event("No snapshot available for validation")
                    return False

                # Validate basic integrity
                if not self._validate_memory_addresses(current_state):
                    return False

                # Process integrity check
                if not self._check_process_integrity():
                    return False

                # Compare current state against snapshot
                current_fingerprint = self._generate_memory_fingerprint(
                    self._serialize_game_state(current_state)
                )
                
                # Check for suspicious patterns in state changes
                if self._detect_suspicious_patterns(current_state):
                    return False

                # Validate state transition legitimacy
                if not self._validate_state_transition(current_state):
                    return False

                return True

            except Exception as e:
                self._log_security_event(f"Validation error: {str(e)}")
                return False

    def _detect_suspicious_patterns(self, current_state):
        """Detect suspicious patterns in state changes"""
        try:
            # Check for rapid score increases
            if 'score' in current_state and 'score' in self.snapshot_data['state']['state_data']:
                score_diff = current_state['score'] - self.snapshot_data['state']['state_data']['score']
                if score_diff > 1000:  # Arbitrary threshold
                    self._log_security_event(f"Suspicious score increase: {score_diff}")
                    return True

            # Check for impossible state transitions
            if 'board' in current_state and 'board' in self.snapshot_data['state']['state_data']:
                changes = sum(1 for i, row in enumerate(current_state['board'])
                            for j, cell in enumerate(row)
                            if cell != self.snapshot_data['state']['state_data']['board'][i][j])
                if changes > 4:  # More changes than possible in one move
                    self._log_security_event(f"Too many board changes: {changes}")
                    return True

            return False

        except Exception as e:
            self._log_security_event(f"Pattern detection error: {str(e)}")
            return True

    def _validate_state_transition(self, current_state):
        """Validate the legitimacy of state transitions"""
        try:
            if not self.snapshot_data.get('state'):
                return True  # First run

            old_state = self.snapshot_data['state']['state_data']
            
            # Validate score changes
            if 'score' in current_state and 'score' in old_state:
                score_diff = current_state['score'] - old_state['score']
                if score_diff > 0:
                    # Log suspicious score changes for pattern analysis
                    self.suspicious_activities['score_changes'].append({
                        'time': time.time(),
                        'diff': score_diff
                    })
                    
                    # Check for suspicious patterns in score changes
                    if self._analyze_score_patterns():
                        return False

            return True

        except Exception as e:
            self._log_security_event(f"State transition validation error: {str(e)}")
            return False

    def _analyze_score_patterns(self):
        """Analyze patterns in score changes for suspicious activity"""
        try:
            recent_changes = [
                change for change in self.suspicious_activities['score_changes']
                if time.time() - change['time'] < 60  # Look at last minute
            ]
            
            if len(recent_changes) > 10:
                # Calculate average time between changes
                times = [change['time'] for change in recent_changes]
                avg_interval = sum(b-a for a, b in zip(times[:-1], times[1:])) / (len(times)-1)
                
                # If changes are too regular or too frequent, flag as suspicious
                if avg_interval < 0.1 or all(abs(b-a - avg_interval) < 0.01 
                                           for a, b in zip(times[:-1], times[1:])):
                    self._log_security_event("Suspicious score change pattern detected")
                    return True
                    
            return False

        except Exception as e:
            self._log_security_event(f"Score pattern analysis error: {str(e)}")
            return True

    def _log_security_event(self, message):
        """Log security-related events with timestamp"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] SECURITY EVENT: {message}\n"
        
        try:
            with open('security_log.txt', 'a') as f:
                f.write(log_entry)
        except Exception:
            pass  # Fail silently if unable to write to log

class MemoryProtector:
    def __init__(self):
        self.scanner = MemorySnapshot()
        self.monitoring = False
        self.monitor_thread = None
        self.last_check = time.time()
        self.check_interval = 1.0  # Check every second
        
    def start_monitoring(self, game_state):
        """Start continuous memory monitoring"""
        if not self.monitoring:
            self.scanner.create_snapshot(game_state)
            self.monitoring = True
            self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            
    def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring:
            time.sleep(0.1)  # Avoid excessive CPU usage
            current_time = time.time()
            if current_time - self.last_check >= self.check_interval:
                self.last_check = current_time
                if not self._check_system_integrity():
                    self._handle_integrity_violation()
                    
    def _check_system_integrity(self):
        """Check system-wide integrity"""
        try:
            # Check for suspicious processes
            for proc in psutil.process_iter(['name', 'cmdline']):
                try:
                    proc_info = proc.info
                    if any(sus in str(proc_info).lower() for sus in 
                          ['cheat', 'inject', 'debug', 'memory', 'hack']):
                        self._log_security_event(f"Suspicious process detected: {proc_info['name']}")
                        return False
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            return True
            
        except Exception as e:
            self._log_security_event(f"System integrity check error: {str(e)}")
            return False
            
    def _handle_integrity_violation(self):
        """Handle detected integrity violations"""
        self._log_security_event("System integrity violation detected")
        # Trigger game termination or state restoration
        self.stop_monitoring()
        # Additional handling can be added here
        
    def _log_security_event(self, message):
        """Log security events"""
        self.scanner._log_security_event(message)

    def validate_current_state(self, game_state):
        """Validate current game state"""
        return self.scanner.validate_state(game_state)

    def update_snapshot(self, game_state):
        """Update the memory snapshot"""
        return self.scanner.create_snapshot(game_state)