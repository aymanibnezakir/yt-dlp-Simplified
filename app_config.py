# app_config.py
"""
Centralized configuration for binary paths and dependency checks.
"""

import sys
import os
import subprocess
from typing import NamedTuple, List

class BinPaths(NamedTuple):
    """
    A simple structure to hold paths to the binaries.
    
    Attributes:
        yt_dlp (str): The path to the yt-dlp binary.
        ffmpeg (str): The path to the ffmpeg binary.
    """
    yt_dlp: str
    ffmpeg: str

def get_platform_paths() -> BinPaths:
    """Gets the platform-specific paths for binaries."""
    if sys.platform == 'linux':
        return BinPaths(
            yt_dlp="./bins/yt-dlp_linux",
            ffmpeg="./bins/ffmpeg-linux"
        )
    elif sys.platform == 'win32':
        return BinPaths(
            yt_dlp=".\\bins\\yt-dlp.exe",
            ffmpeg=".\\bins\\ffmpeg.exe"
        )
    else:
        # A basic fallback for other systems (e.g., macOS)
        # Currently unsupported.
        return BinPaths(
            yt_dlp="./bins/yt-dlp",
            ffmpeg="./bins/ffmpeg"
        )

DEPENDENCY_PATHS = get_platform_paths()


def check_dependencies() -> List[str]:
    """
    Checks for existence and permissions of required binaries.
    Tries to fix permissions on Linux.
    
    Returns:
        A list of error strings if any problems are found. An empty
        list indicates success.
    """
    problems = []

    for name, path in DEPENDENCY_PATHS._asdict().items():
        if not os.path.exists(path):
            problems.append(f"Missing executable: {path}")
            continue
        
        # Special check for Linux: ensure it's executable
        if sys.platform == 'linux' and not os.access(path, os.X_OK):
            try:
                subprocess.run(['chmod', '+x', path], check=True)
                
                # Re-check permission after attempting to fix
                if not os.access(path, os.X_OK):
                    problems.append(f"Permission error: Could not make {path} executable.")
            except Exception as e:
                problems.append(f"Permission error on {path}: {e}")

    return problems