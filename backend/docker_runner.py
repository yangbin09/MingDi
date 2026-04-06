"""
Docker Sandbox Runner for 鸣镝
Runs sensitive tasks in isolated Docker containers
"""
import os
import time
import tempfile
import logging
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)


def check_docker_available() -> bool:
    """Check if Docker is available"""
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True
    except Exception as e:
        logger.warning(f"Docker not available: {e}")
        return False


def run_in_docker(
    code: str,
    requirements: List[str] = None,
    docker_image: str = "python:3.11-slim",
    timeout: int = 60,
    environment: dict = None
) -> Tuple[bool, str, int, float]:
    """
    Run Python code in an isolated Docker container

    Returns: (success, output, exit_code, execution_time)
    """
    if not check_docker_available():
        return False, "Docker is not available on this system", -1, 0

    import docker

    start_time = time.time()
    requirements = requirements or []

    # Create temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write code to file
        code_path = os.path.join(tmpdir, "script.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Create requirements.txt if needed
        if requirements:
            req_path = os.path.join(tmpdir, "requirements.txt")
            with open(req_path, "w") as f:
                f.write("\n".join(requirements))

        # Build docker command
        cmd = ["python", "script.py"]
        if requirements:
            # Install requirements first
            install_cmd = ["pip", "install", "-q"] + requirements
            full_cmd = ["sh", "-c", " && ".join([" ".join(install_cmd)] + [" ".join(cmd)])]
        else:
            full_cmd = cmd

        try:
            client = docker.from_env()

            # Run container
            container = client.containers.run(
                docker_image,
                command=full_cmd,
                volumes={tmpdir: {"bind": "/code", "mode": "rw"}},
                working_dir="/code",
                environment=environment or {},
                detach=True,
                mem_limit="512m",
                cpu_period=100000,
                cpu_quota=50000,  # 50% CPU
                pids_limit=64,
                network_mode="none",  # No network access for security
                remove=False,
                stderr=True,
                stdout=True
            )

            # Wait for completion with timeout
            result = container.wait(timeout=timeout)

            # Get output
            output = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")

            # Cleanup
            container.remove(force=True)

            execution_time = time.time() - start_time
            exit_code = result.get("StatusCode", -1)

            return exit_code == 0, output, exit_code, execution_time

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Docker execution error: {e}")
            return False, f"Docker execution error: {str(e)}", -1, execution_time


def extract_requirements_from_code(code: str) -> List[str]:
    """
    Extract Python package requirements from code imports
    """
    import re

    # Standard library modules to exclude
    stdlib = {
        "os", "sys", "time", "datetime", "timedelta", "date",
        "re", "json", "csv", "io", "StringIO", "cStringIO",
        "math", "random", "hashlib", "hmac", "secrets",
        "collections", "abc", "functools", "itertools",
        "gc", "weakref", "types", "copy", "pickle", "shelve",
        "struct", "codecs", "unicodedata", "locale", "gettext",
        "argparse", "optparse", "subprocess", "threading",
        "multiprocessing", "asyncio", "concurrent", "queue",
        "socket", "ssl", "http", "http.client", "http.server",
        "urllib", "urllib.request", "urllib.parse", "urllib.error",
        "ftplib", "smtplib", "poplib", "imaplib", "nntplib",
        "telnetlib", "ssh", "paramiko",
        "sqlite3", "dbm", "gdbm", "anydbm", "whichdb",
        "xml", "xml.etree", "xml.dom", "xml.sax",
        "html", "html.parser", "html.entities",
        "cgi", "wsgiref", "webbrowser",
        "zipfile", "tarfile", "gzip", "bz2", "lzma", "zipimport",
        "base64", "binascii", "binhex",
        "plistlib", "macpath", "macurl2path",
        "fileinput", "stat", "statvfs", "filecmp", "difflib",
        "tempfile", "glob", "fnmatch", "linecache", "shutil", "disk_usage",
        "pathlib", "posixpath", "ntpath", "genericpath", "os.path",
        "inspect", "traceback", "dis", "pickletools",
        "compileall", "py_compile", "compile", "code", "codeop",
        "print", "input",
        "platform", "errno", "ctypes", "signal", "mmap",
        "msvcrt", "termios", "tty", "pty", "fcntl", "resource",
        "logging", "logging.handlers", "warnings", "audit", "atexit",
        "contextlib", "abc", "dataclasses", "field", "fields", "asdict",
        "typing", "typing.io", "typing.re", "typing_extensions",
        "enum", "IntEnum", "Flag", "IntFlag", "auto",
        "textwrap", "string", "unicodedata",
        "spell", "textwrap",
        "formatter",
    }

    requirements = set()
    import_patterns = [
        r'^import\s+(\w+)',
        r'^from\s+(\w+)\s+import',
    ]

    for line in code.split('\n'):
        line = line.strip()
        if line.startswith('#') or line.startswith('"""') or line.startswith("'''"):
            continue

        for pattern in import_patterns:
            match = None
            if pattern.startswith('^'):
                match = re.match(pattern, line)
            else:
                match = re.search(pattern, line)

            if match:
                module = match.group(1) if match.group(1) else match.group(2) if match.group(2) else None
                if module and module not in stdlib:
                    # Common package name mappings
                    if module == "PIL":
                        requirements.add("Pillow")
                    elif module == "sklearn":
                        requirements.add("scikit-learn")
                    elif module == "cv2":
                        requirements.add("opencv-python")
                    elif module == "plt":
                        requirements.add("matplotlib")
                    elif module == "np":
                        requirements.add("numpy")
                    elif module == "pd":
                        requirements.add("pandas")
                    elif module == "pd":
                        requirements.add("pandas")
                    elif module == "sp":
                        requirements.add("scipy")
                    elif module == "tf":
                        requirements.add("tensorflow")
                    elif module == "torch":
                        requirements.add("torch")
                    elif module == "ks":
                        requirements.add("keplergl")
                    elif module == "px":
                        requirements.add("plotly")
                    elif module == "sns":
                        requirements.add("seaborn")
                    elif module == "jwt":
                        requirements.add("PyJWT")
                    elif module == "yaml":
                        requirements.add("PyYAML")
                    elif module == "mysql":
                        requirements.add("pymysql")
                    elif module == "psycopg2":
                        requirements.add("psycopg2-binary")
                    elif module == "kafka":
                        requirements.add("kafka-python")
                    elif module == "elasticsearch":
                        requirements.add("elasticsearch")
                    elif module == "redis":
                        requirements.add("redis")
                    elif module == "mongo":
                        requirements.add("pymongo")
                    elif module == "grpc":
                        requirements.add("grpcio")
                    elif module == "nanoid":
                        requirements.add("nanoid")
                    else:
                        requirements.add(module.lower())

    return sorted(list(requirements))


# Export for use in other modules
DOCKER_AVAILABLE = check_docker_available()
