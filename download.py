"""This module contains the Download class, which is responsible for handling the download process.

Classes:
    - Download: A class that encapsulates the download logic.
"""
import os
import sys
import subprocess
from typing import Callable
from app_config import DEPENDENCY_PATHS

class Download:
    """A class to represent a download operation.

    Attributes:
        link (str): The URL of the video to download.
        aud_only (bool): A flag to indicate whether to download only the audio.
        save_path (str): The directory where the downloaded file will be saved.
        yt_dlp_exe (str): The path to the yt-dlp executable.
        ffmpeg_loc (str): The path to the ffmpeg executable.
    """
    def __init__(self, link: str, aud_only: bool, save_path: str) -> None:
        self.link = link
        self.aud_only = aud_only
        # This is now the SAVE DIRECTORY
        self.save_path = save_path

        # --- MODIFIED: Use centralized paths ---
        self.yt_dlp_exe = DEPENDENCY_PATHS.yt_dlp
        self.ffmpeg_loc = DEPENDENCY_PATHS.ffmpeg

    
    def verifyLink(self) -> bool:
        """ Verifies if the input string is a link (expanded for flexibility) """
        if (self.link.startswith('https://') or self.link.startswith('http://')):
             return True
        if (self.link.startswith('https://www.') or self.link.startswith('http://www.')) and len(self.link) > 15:
            return True
        return False
    
    # --- REMOVED: _prepare_save_path method ---
    # (This method was already removed in your original file)

    # --- MODIFIED: _build_command method ---
    def _build_command(self) -> list[str]:
        """Builds the yt-dlp command list based on user options."""
        
        # --- NEW: Build output template ---
        # self.save_path is the directory (e.g., "C:/Users/Me/Videos")
        # yt-dlp will replace %(title)s with the video title and
        # %(ext)s with the correct extension (mp3 or mp4).
        # os.path.join handles Windows (\) vs. Linux (/) slashes.
        output_template = os.path.join(self.save_path, "%(title)s.%(ext)s")
        # --- END NEW ---

        # Base command with essential flags for good console output
        cmd = [
            self.yt_dlp_exe,
            "--ffmpeg-location", self.ffmpeg_loc,
            "--progress",       # Show progress in output
            "--newline",        # Ensure progress is on new lines
            # Removed "--force-overwrites". 
            # Default yt-dlp behavior is to overwrite if a final file exists.
        ]

        if self.aud_only:
            # Audio-only command
            cmd.extend([
                "-x",  # Extract audio
                "--audio-format", "mp3",
                "-o", output_template, # Set output template
                self.link
            ])
        else:
            # Video command (best video + best audio, merge to mp4)
            cmd.extend([
                "-f", "bestvideo+bestaudio",
                "--merge-output-format", "mp4",
                "-o", output_template, # Set output template
                self.link
            ])
            
        return cmd
    # --- END MODIFICATION ---

    def run_download(self, status_callback: Callable[[str], None]):
        """
        Runs the yt-dlp download command and sends real-time output
        to the provided callback function.
        """
        try:
            cmd = self._build_command()
        except Exception as e:
            status_callback(f"Error building command: {e}")
            return

        # Hide console window on Windows
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

        try:
            # Start the subprocess
            with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=creation_flags
            ) as proc:
                if proc.stdout is not None:
                    # Read output line by line in real-time
                    for line in proc.stdout:
                        if "Unknown" in line.strip():
                            continue
                        status_callback(f"[yt-dlp] {line.strip()}")
                
                proc.wait() # Wait for the process to finish
                if proc.returncode != 0:
                    status_callback(f"[yt-dlp] Process exited with error code: {proc.returncode}")
                else:
                    status_callback(f"[yt-dlp] Download successful!")

        except FileNotFoundError:
            status_callback(f"Error: Executable not found at {self.yt_dlp_exe}")
        except Exception as e:
            status_callback(f"An unexpected error occurred: {e}")