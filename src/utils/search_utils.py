import time
import timeout_decorator
from typing import Callable, List, Any, Optional, Tuple


def with_timeout(timeout: int, exception=TimeoutError):
    """Decorator factory to apply timeout_decorator with a specified timeout."""

    def decorator(func: Callable) -> Callable:
        @timeout_decorator.timeout(timeout, timeout_exception=exception)
        def wrapper(*args, **kwargs) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator


class TimeoutRunner:
    """Manages execution of search algorithms with configurable timeouts."""

    def __init__(self, default_timeout: int = 5):
        """Initialize with a default timeout in seconds."""
        self.default_timeout = default_timeout

    def _run_single(self, algorithm: Callable, problem: Any, heuristic: Optional[Callable] = None, timeout: int = 5) -> \
    Tuple[Any, int, int]:
        """Run a single search algorithm on a problem with an optional heuristic."""

        @with_timeout(timeout)
        def execute():
            if heuristic is not None:
                return algorithm(problem, heuristic)
            return algorithm(problem)

        return execute()

    def run(self, algorithm: Callable, problems: List[Any], heuristic: Optional[Callable] = None,
            timeout: Optional[int] = None) -> Tuple[List[Any], List[int], List[int], List[float], int]:
        """Run an algorithm on a list of problems, tracking metrics."""
        timeout = timeout or self.default_timeout
        solutions = []
        visited_nodes = []
        depths = []
        times = []
        failures = 0

        for problem in problems:
            try:
                start_time = time.time()
                solution, num_visited, depth = self._run_single(algorithm, problem, heuristic, timeout)
                solutions.append(solution)
                visited_nodes.append(num_visited)
                depths.append(depth)
                times.append(time.time() - start_time)
            except TimeoutError:
                failures += 1

        return solutions, visited_nodes, depths, times, failures