import time
import logging
from functools import wraps

# Configure performance logger
perf_logger = logging.getLogger('performance')
perf_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
perf_logger.addHandler(handler)

def monitor_performance(func):
    """Decorator to measure and log function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        perf_logger.info(
            f"{func.__module__}.{func.__name__} executed in {duration_ms:.2f}ms",
            extra={'duration_ms': duration_ms}
        )
        return result
    return wrapper

class PerformanceMetrics:
    """Context manager for measuring code block performance"""
    def __init__(self, name):
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        duration_ms = (end_time - self.start_time) * 1000
        perf_logger.info(
            f"{self.name} executed in {duration_ms:.2f}ms",
            extra={'operation': self.name, 'duration_ms': duration_ms}
        )