"""This module contains the Update class, which is responsible for updating the yt-dlp executable."""

import sys
import subprocess
from typing import Callable
from app_config import DEPENDENCY_PATHS


class Update:
    """A class to represent an update operation.

    Attributes:
        name (str): The path to the yt-dlp executable.
    """
    def __init__(self) -> None:
        self.name = DEPENDENCY_PATHS.yt_dlp

  
    def update(self, status_callback: Callable[[str], None]):
        """
        Runs the yt-dlp update command and sends real-time output
        to the provided callback function.
        """
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

        try:
            with subprocess.Popen(
                [self.name, "-U"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=creation_flags
            ) as proc:
                if proc.stdout is not None:
                    for line in proc.stdout:
                        status_callback(f"[yt-dlp] {line.strip()}")
                
                proc.wait()
                if proc.returncode != 0:
                    status_callback(f"[yt-dlp] Process exited with error code: {proc.returncode}")

        except FileNotFoundError:
            status_callback(f"Error: Executable not found at {self.name}")
        except Exception as e:
            status_callback(f"An unexpected error occurred: {e}")