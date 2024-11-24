from pathlib import Path
from loguru import logger
import subprocess
from datetime import datetime

__all__ = [
    "setEnvVar",
    "add_reminder",
]


def setEnvVar(key: str, value: str) -> None:
    key = key.upper()
    path = (Path.cwd() / ".env").resolve()
    try:
        with open(path, "r") as f:
            env = f.readlines()
    except IOError as e:
        logger.critical(f"Permission denied, Try re-run the program by using 'sudo'")
        raise e
    except Exception as e:
        logger.critical(f"Unexpected error occurred while parsing '{f}'")
        raise e

    found = False
    updatedEnv = []
    for line in env:
        if line.startswith(key + "="):
            updatedEnv.append(f'{key}="{value}"\n')
            found = True
        else:
            updatedEnv.append(line)

    if not found:
        updatedEnv.append(f'{key}="{value}"\n')

    try:
        with open(path, "w") as f:
            f.writelines(updatedEnv)
    except IOError as e:
        logger.critical(f"Permission denied, Try re-run the program by using 'sudo'")
        raise e
    except Exception as e:
        logger.critical(f"Unexpected error occurred while parsing '{f}'")
        raise e


def add_reminder(name: str, dueDate: datetime):
    """Add a reminder to the system."""
    dueDate = dueDate.strftime("%Y-%m-%d %H:%M:%S")

    script = f"""
    tell application "Reminders"
        make new reminder with properties {{name:"{name}", due date:(current date) + 5 * days}}
    end tell
    """

    subprocess.run(["osascript", "-e", script])
