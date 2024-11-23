from pathlib import Path

from loguru import logger

__all__ = [
    "setEnvVar",
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
