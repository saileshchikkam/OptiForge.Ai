from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import tempfile
import time


@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    return_code: int
    runtime: float
    phase: str


def run_python_code(code: str, input_data: str = "") -> ExecutionResult:
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "main.py"
        source.write_text(code, encoding="utf-8")
        start = time.perf_counter()
        try:
            result = subprocess.run(
                [sys.executable, str(source)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return ExecutionResult(
                result.returncode == 0,
                result.stdout,
                result.stderr,
                result.returncode,
                time.perf_counter() - start,
                "execution",
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(False, "", "Execution timed out.", -1, time.perf_counter() - start, "execution")


def run_cpp_code(code: str, input_data: str = "") -> ExecutionResult:
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "main.cpp"
        exe = Path(temp_dir) / "main.exe"
        source.write_text(code, encoding="utf-8")

        try:
            compile_result = subprocess.run(
                ["g++", "-std=c++17", "-O2", str(source), "-o", str(exe)],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except FileNotFoundError:
            return ExecutionResult(False, "", "g++ was not found on PATH.", -1, 0.0, "compilation")

        if compile_result.returncode != 0:
            return ExecutionResult(
                False, "", compile_result.stderr, compile_result.returncode, 0.0, "compilation"
            )

        start = time.perf_counter()
        try:
            result = subprocess.run(
                [str(exe)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return ExecutionResult(
                result.returncode == 0,
                result.stdout,
                result.stderr,
                result.returncode,
                time.perf_counter() - start,
                "execution",
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(False, "", "Execution timed out.", -1, time.perf_counter() - start, "execution")


def run_java_code(code: str, input_data: str = "") -> ExecutionResult:
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "Main.java"
        source.write_text(code, encoding="utf-8")

        try:
            compile_result = subprocess.run(
                ["javac", str(source)],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except FileNotFoundError:
            return ExecutionResult(False, "", "javac was not found on PATH.", -1, 0.0, "compilation")

        if compile_result.returncode != 0:
            return ExecutionResult(
                False, "", compile_result.stderr, compile_result.returncode, 0.0, "compilation"
            )

        start = time.perf_counter()
        try:
            result = subprocess.run(
                ["java", "-cp", temp_dir, "Main"],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return ExecutionResult(
                result.returncode == 0,
                result.stdout,
                result.stderr,
                result.returncode,
                time.perf_counter() - start,
                "execution",
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(False, "", "Execution timed out.", -1, time.perf_counter() - start, "execution")


EXECUTORS = {
    "python": run_python_code,
    "cpp": run_cpp_code,
    "java": run_java_code,
}


def run_code(code: str, language: str, input_data: str = "") -> ExecutionResult:
    if language not in EXECUTORS:
        raise ValueError(f"No executor available for: {language}")
    return EXECUTORS[language](code, input_data)
