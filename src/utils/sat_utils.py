import time
import subprocess
import os
import timeout_decorator
from typing import Callable, Any

def with_timeout(timeout: int, exception=TimeoutError):
    """Decorator factory to apply timeout_decorator with a specified timeout."""
    def decorator(func: Callable) -> Callable:
        @timeout_decorator.timeout(timeout, timeout_exception=exception)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TimeoutError:
                raise TimeoutError
        return wrapper
    return decorator

def run_dpll_algorithm(
    algorithm: Callable,
    input_data: Any,
    timeout: int = 20
) -> Any:
    """Run a DPLL algorithm with a configurable timeout."""
    @with_timeout(timeout)
    def run_with_timeout():
        return algorithm(input_data)
    return run_with_timeout()

def run_minisat_command(
    minisat_path: str = "../../external/minisat",
    input_file: str = "example.cnf",
    output_file: str = "tests.out",
    timeout: int = 20
) -> None:
    """Run MiniSAT with a configurable timeout, suppressing output."""
    @with_timeout(timeout)
    def run_with_timeout():
        with open(os.devnull, 'w') as devnull:
            subprocess.call([minisat_path, input_file, output_file], stdout=devnull, stderr=devnull)
    run_with_timeout()

def run_sat_solver(
    minisat_path: str = "../../external/minisat",
    input_file: str = "example.cnf",
    output_file: str = "tests.out",
    timeout: int = 20
) -> float:
    """Measure time taken to run MiniSAT, handling timeouts."""
    try:
        start_time = time.time()
        run_minisat_command(minisat_path, input_file, output_file, timeout)
        return time.time() - start_time
    except TimeoutError:
        raise TimeoutError