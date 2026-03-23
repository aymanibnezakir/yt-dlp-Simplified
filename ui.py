""" Core UI module of the program.
    Also, the main entry point for the program."""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
from ttkthemes import ThemedTk
import threading
import webbrowser
import subprocess
import os
import sys
import download as download_module
import update_ytdlp
import configManager as cfm
import app_config

from version import __version__
import self_updater



class Window:
    """The main window of the application.

    Attributes:
        version (str): The version of the application.
        root (tk.Tk): The root window of the application.
        urlEntry (ttk.Entry): The entry for the URL.
        browseBtn (ttk.Button): The button to browse for a save location.
        locationEntry (ttk.Entry): The entry for the save location.
        audOnly (tk.BooleanVar): A variable to indicate whether to download only the audio.
        audOnlyBtn (ttk.Checkbutton): The checkbutton to select audio-only download.
        dwnBtn (ttk.Button): The button to start the download.
        updEngineBtn (ttk.Button): The button to update yt-dlp.
        console_scrollbar (ttk.Scrollbar): The scrollbar for the console output.
        console_output (tk.Text): The text widget for the console output.
    """
    def __init__(self) -> None:
        self.version = __version__
        self.root = ThemedTk(theme="yaru")
        self.root.title(f"yt-dlp Simplified {self.version}")
        self.root.iconbitmap("icon.ico")

        self._pending_logs = []
        def _cfm_logger(text):
            if hasattr(self, 'console_output'):
                self.append_to_console(text)
            else:
                self._pending_logs.append(text)

        cfm.set_logger(_cfm_logger)

        self.root.geometry('600x600')

        self.root.resizable(False, False)


        try:
            scaling = float(self.root.tk.call("tk", "scaling"))
        except Exception:
            scaling = 1.0
        default_font = font.nametofont("TkDefaultFont")
        base_size = max(9, int(default_font.cget("size") * scaling))
        default_font.configure(size=base_size)


        container = ttk.Frame(self.root, padding=(10, 10))
        container.pack(fill="both", expand=True)

        container.rowconfigure(3, weight=1)
        container.columnconfigure(1, weight=1)
        
        
        # URL Entry
        self.urlEntry = ttk.Entry(container)
        self.urlEntry.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        
        placeholder_text = "Enter or paste an URL"
        self.urlEntry.insert(0, placeholder_text)
        self.urlEntry.config(foreground="gray", justify="center")

        def on_focus_in(event):
            if self.urlEntry.get() == placeholder_text:
                self.urlEntry.delete(0, tk.END)
                self.urlEntry.config(foreground="black", justify="left")

        def on_focus_out(event):
            if not self.urlEntry.get():
                self.urlEntry.config(justify="center")
                self.urlEntry.insert(0, placeholder_text)
                self.urlEntry.config(foreground="gray")
            else:
                self.urlEntry.xview_moveto(0)

        def on_after_paste(event):
            def focus_start():
                self.urlEntry.xview_moveto(0)
                self.urlEntry.icursor(0)
            self.urlEntry.after(10, focus_start)

        self.urlEntry.bind("<FocusIn>", on_focus_in)
        self.urlEntry.bind("<FocusOut>", on_focus_out)
        self.urlEntry.bind("<<Paste>>", on_after_paste)
        self.urlEntry.bind("<Return>", lambda e: self.download())


        dat = ""

        if cfm.getKeyValue("path") != None:
            dat = cfm.getKeyValue("path")
        else:
            cfm.setDefaultParams()
            dat = ""

        self.browseBtn = ttk.Button(container,
                                    text="Choose Location" if dat == "" else "Change Location",
                                    command=self.browse)
        self.browseBtn.grid(row=1, column=0, sticky="w", padx=(0, 8))

        self.locationEntry = ttk.Entry(container, state="disabled", justify="center")
        self.locationEntry.grid(row=1, column=1, sticky="ew")
        self.updLocEntry(dat) # type: ignore


        self.audOnly = tk.BooleanVar(value=False)
        self.audOnlyBtn = ttk.Checkbutton(container, text="Save as mp3", variable=self.audOnly)
        self.audOnlyBtn.grid(row=2, column=0, sticky="w", pady=(8, 0))


        self.ignorePlaylist = tk.BooleanVar(value=False)
        self.ignorePlaylistBtn = ttk.Checkbutton(container, text="Ignore Playlist", variable=self.ignorePlaylist)
        self.ignorePlaylistBtn.grid(row=2, column=1, sticky="w", pady=(8, 0))


        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8, 0))


        self.dwnBtn = ttk.Button(btn_frame, text="Download", command=self.download)
        self.dwnBtn.pack(side="right")


        self.updEngineBtn = ttk.Button(btn_frame, text="Update Engine", command=self.updDlp)
        self.updEngineBtn.pack(side="right", padx=(0, 8))


        console_frame = ttk.Frame(container)
        console_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)

        self.console_scrollbar = ttk.Scrollbar(console_frame, orient="vertical")
        self.console_output = tk.Text(
            console_frame,
            wrap="word",
            state="disabled",
            yscrollcommand=self.console_scrollbar.set,
            height=5,
            width=10
        )
        self.console_scrollbar.config(command=self.console_output.yview)


        self.console_output.grid(row=0, column=0, sticky="nsew")
        self.console_scrollbar.grid(row=0, column=1, sticky="ns")

        self.append_to_console(f"yt-dlp Simplified {self.version}\nNot intended for any unethical purpose.\nAuthor: Ayman Ibne Zakir (github.com/aymanibnezakir)\n")
        self.append_to_console("Note: If a download fails, try updating the engine.\n")
        
        for log in self._pending_logs:
            self.append_to_console(log)
        self._pending_logs.clear()
        
        self.create_menu()

        self.run_startup_checks()

    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File Menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Settings", command=self.open_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        # Help Menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label="Check for updates", command=self.check_for_updates)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="About", command=self.show_about)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="Github", command=self.open_github)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)

    def open_settings(self):
        messagebox.showinfo("Settings", "Settings feature coming soon!")
        return 

        # TODO: Implement settings

    def show_about(self):
        messagebox.showinfo("About", f"yt-dlp Simplified {self.version}\nAuthor: Ayman Ibne Zakir\n\nA simple UI for yt-dlp.")

    def open_github(self):
        webbrowser.open("https://github.com/aymanibnezakir/yt-dlp-Simplified")

    def check_for_updates(self):
        self.disable_buttons()
        
        threading.Thread(
            target=self.run_update_check_thread,
            daemon=True
        ).start()

    def run_update_check_thread(self):
        """Worker thread for checking updates."""
        try:
            upd = self_updater.Updater()
            result = upd.check_for_update()
            if result:
                self.append_to_console("Update started, closing window...")
                self.root.destroy() 
        except Exception as e:
            messagebox.showerror("Error", f"Update check failed: {e}")
        finally:
            self.root.after(0, self.enable_buttons)

    def updLocEntry(self, txt: str):
        self.locationEntry.config(state="normal")
        self.locationEntry.delete(0, tk.END)
        if txt:
            self.locationEntry.insert(0, txt)
        self.locationEntry.config(state="disabled")


    def browse(self):
        """
        Opens a dialog for the user to select a save *directory*.
        """

        path = filedialog.askdirectory(
            title="Choose save location..."
        )
        
        if not path:
            return

        self.updLocEntry(path)
        self.browseBtn.config(text="Change Location")
        try:
            cfm.writeCfg("path", path)
        except Exception:
            messagebox.showwarning("Warning", "Could not save location.")

    
    def append_to_console(self, text: str):
        """
        Appends a line of text to the console output area.
        This method is thread-safe as it schedules the update on the main GUI thread.
        """
        def _append():
            self.console_output.config(state="normal")
            self.console_output.insert(tk.END, text + "\n")
            self.console_output.config(state="disabled")
            self.console_output.see(tk.END) # Auto-scroll
        
        self.last_line_was_progress = False
        self.root.after(0, _append)

    def replace_last_console_line(self, text: str):
        """
        Replaces the previous line of text in the console with new text.
        This provides in-place updates for repetitive output like download progress.
        """
        def _replace():
            self.console_output.config(state="normal")
            # Delete the contents of the last inserted line (which is at end-2l because of tk's trailing newline)
            if int(self.console_output.index('end-1c').split('.')[0]) > 1:
                self.console_output.delete("end-2l", "end-2l lineend")
            # Insert the new text at the same line
            self.console_output.insert("end-2l", text)
            self.console_output.config(state="disabled")
            self.console_output.see(tk.END)
            
        self.root.after(0, _replace)

    def disable_buttons(self):
        """Disables buttons during an operation."""
        self.dwnBtn.config(state="disabled")
        self.updEngineBtn.config(state="disabled")
        self.help_menu.entryconfig(0, state="disabled")

    def enable_buttons(self):
        """Enables buttons after an operation."""
        self.dwnBtn.config(state="normal")
        self.updEngineBtn.config(state="normal")
        self.help_menu.entryconfig(0, state="normal")
    
    
    def run_startup_checks(self):
        """Runs dependency checks and initial update check."""
        self.append_to_console("Executing file check...")
        
        problems = app_config.check_dependencies()
        
        if not problems:
            self.append_to_console("Dependencies found & standby...\n")
            
        else:
            for item in problems:
                self.append_to_console(f"Error: {item}")
            self.append_to_console("Error: Add missing files to the bins folder or fix permissions.")
            self.disable_buttons() 
            self.append_to_console("All operations disabled until dependencies are fixed.")


    def updDlp(self):
        update_handler = update_ytdlp.Update()       
        self.disable_buttons()
        self.append_to_console("Initializing engine update...")
        
        threading.Thread(
            target=self.run_update_thread, 
            args=(update_handler,), 
            daemon=True
        ).start()

    
    def run_update_thread(self, update_handler: update_ytdlp.Update):
        """Worker thread for running the update process."""
        try:
            update_handler.update(self.append_to_console)
        except Exception as e:
            self.append_to_console(f"Update failed: {e}")
        finally:
            self.root.after(0, self.enable_buttons)

    
    def download(self):
        url = self.urlEntry.get().strip()
        if url == "Enter or paste URL":
            url = ""
        save_path = self.locationEntry.get().strip() 
        aud_only = self.audOnly.get()
        ignore_playlist = self.ignorePlaylist.get()

        # --- Validation ---
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            return

        if not save_path:
            messagebox.showerror("Error", "Please choose a save location (directory).")
            return
        
        # Playlist warning
        if not ignore_playlist and "list=" in url:
            result = messagebox.askyesno("Playlist Warning", "The URL refers to a video and a playlist. Do you want to download the video only?")
            if result:
                ignore_playlist = True
             

        # Use a temporary handler just for validation
        validator = download_module.Download(url, aud_only, ignore_playlist, save_path)
        if not validator.verifyLink():
            messagebox.showerror("Error", "Invalid URL provided.")
            return
        
        # --- Start Download Thread ---
        self.disable_buttons()
        self.append_to_console(f"Starting download for: {url}")
        
        # Create the real handler for the thread
        download_handler = download_module.Download(url, aud_only, ignore_playlist, save_path)
        
        threading.Thread(
            target=self.run_download_thread, 
            args=(download_handler,), 
            daemon=True
        ).start()

    
    def run_download_thread(self, download_handler: download_module.Download):
        """Worker thread for running the download process."""
        try:
            # Pass the console append method as a callback
            def console_manager(line: str, is_progress: bool = False):
                if is_progress:
                    if self.last_line_was_progress:
                        self.replace_last_console_line(line)
                    else:
                        self.append_to_console(line)
                        self.last_line_was_progress = True
                else:
                    self.append_to_console(line)

            download_handler.run_download(console_manager)
        except Exception as e:
            self.append_to_console(f"Download failed: {e}")
        finally:
            # Re-enable buttons back on the main thread
            self.root.after(0, self.enable_buttons)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        window = Window()
        window.run()
