"""This module contains the Download class, which is responsible for handling the download process.

Classes:
    - Download: A class that encapsulates the download logic.
"""
import os
import sys
import subprocess
import re
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
    def __init__(self, link: str, aud_only: bool, ignore_playlist: bool, save_path: str) -> None:
        self.link = link
        self.aud_only = aud_only
        self.ignore_playlist = ignore_playlist
        self.save_path = save_path

        self.yt_dlp_exe = DEPENDENCY_PATHS.yt_dlp
        self.ffmpeg_loc = DEPENDENCY_PATHS.ffmpeg

    
    def verifyLink(self) -> bool:
        """ Verifies if the input string is a link"""
        if self.link.startswith(('https://', 'http://', 'www.')) and len(self.link) > 10:
             return True

        return False
    

    def _build_command(self) -> list[str]:
        """Builds the yt-dlp command list based on user options."""
        
        output_template = os.path.join(self.save_path, "%(title)s.%(ext)s")

        # Base command with essential flags for good console output
        cmd = [
            self.yt_dlp_exe,
            "--ffmpeg-location", self.ffmpeg_loc,
            "--quiet",
            "--progress",       # Show progress in output
        ]

        if self.ignore_playlist:
            cmd.append("--no-playlist")

        if self.aud_only:
            # Audio-only command
            cmd.extend([
                "-x",  # Extract audio
                "--audio-format", "mp3",
                "-o", output_template,
                self.link
            ])
        else:
            # Video command (best video + best audio, merge to mp4)
            cmd.extend([
                "-f", "bestvideo+bestaudio",
                "--merge-output-format", "mp4",
                "-o", output_template,
                self.link
            ])
            
        return cmd


    def run_download(self, status_callback: Callable[[str, bool], None]):
        """
        Runs the yt-dlp download command and sends real-time output
        to the provided callback function.
        """
        try:
            cmd = self._build_command()
        except Exception as e:
            status_callback(f"Error building command: {e}", False)
            return

        # Hide console window on Windows
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

        try:
            # Start the subprocess
            with subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
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
                        clean_line = line.strip()
                        if "Unknown" in clean_line:
                            continue
                            
                        # yt-dlp's progress output usually looks like "[download]   0.1% of" or "[download] 100% of"
                        is_progress = bool(re.search(r"\[download\]\s+\d+(\.\d+)?%\s+of", clean_line))
                        
                        if clean_line == "":
                            status_callback(f"")
                        else:
                            status_callback(f"[Engine] {clean_line}", is_progress)
                
                proc.wait()
                if proc.returncode != 0:
                    status_callback(f"[Engine] Process exited with error code: {proc.returncode}", False)
                else:
                    status_callback(f"[Engine] Download successful!", False)

        except FileNotFoundError:
            status_callback(f"Error: Executable not found at {self.yt_dlp_exe}", False)
        except Exception as e:
            status_callback(f"An unexpected error occurred: {e}", False)