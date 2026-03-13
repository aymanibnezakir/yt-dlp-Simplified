# yt-dlp Simplified

A simple and easy-to-use graphical user interface (GUI) for the powerful command-line video downloader, [yt-dlp](https://github.com/yt-dlp/yt-dlp). This application allows you to download video/audio from a wide range of websites those are supported by yt-dlp [(see List)](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) without needing to use the command line.  
⚠️ Note: This application only focuses on "simply" downloading video/audio at the highest quality available, and doesn't include advance features of yt-dlp to keep it as simple and lightweight as possible.

## Features

- **Simple Interface:** A clean and straightforward interface for downloading videos.
- **Video and Audio Downloads:** Choose to download the full video or just the audio in MP3 format.
- **Ignore Playlist:** Choose to download a single video from a playlist URL instead of downloading the entire playlist.
- **Save Location:** Select and save your preferred download location.
- **Real-time Console Output:** See the download progress and any messages from `yt-dlp` (engine) in real-time.
- **Built-in Updater:** Keep your `yt-dlp` (engine) up-to-date with a single click.
- **Cross-Platform:** Works on both Windows and Linux.

## How to Use

1.  **Run the application:**
    -   On Windows, run `yt-dlp-Simplified.exe`.
    -   On Linux, run the `yt-dlp-Simplified` executable. (May need to use `chmod +x` command)
2.  **Enter the URL:** Paste the URL of the video you want to download into the "Enter URL" field.
3.  **Choose a Location:** Click "Choose Location" to select a folder where you want to save your download. This location will be saved for future use.
4.  **Select Download Type:**
    -   For a video, leave the "Save as Audio" checkbox unchecked.
    -   For audio, check the "Save as Audio" box.
    -   To download a single video from a playlist URL, check the "Ignore Playlist" box.
5.  **Download:** Click the "Download" button to start the download.

## Dependencies

This application relies on the following external programs, which are included in the `bins` directory:

-   **yt-dlp:** The core video downloading tool.
-   **deno:** The js runtime for yt-dlp.
-   **ffmpeg:** Used for processing and converting video and audio files (e.g., creating MP3s).

The application will automatically check for these files on startup.

## Building from Source

To build this project from the source code, you will need:

-   Python 3
-   The `Nuitka` Python compiler (if you want to create an executable)
-   The `uv` package manager (if you want to create an executable)
-   Run the command: `uv sync` to install dependencies
-   Build the application using the command (On Windows): `python -m nuitka ui.py --standalone --windows-console-mode=disable --enable-plugin=tk-inter --include-package-data=ttkthemes --windows-icon-from-ico=icon.ico --include-data-files=icon.ico=icon.ico --include-data-files=bins/*=bins/ --output-filename="yt-dlp-Simplified.exe"`
-   Build the application using the command (On Linux): `python -m nuitka ui.py --standalone --enable-plugin=tk-inter --include-package-data=ttkthemes --include-data-files=icon.ico=icon.ico --include-data-files=bins/*=bins/ --output-filename="yt-dlp-Simplified"`

You can run the application directly from the source by executing the `ui.py` file:

```bash
uv run ui.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

