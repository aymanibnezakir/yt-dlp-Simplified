""" Core UI module of the program.
    Also, the main entry point for the program."""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
import threading
import download as download_module
import update_ytdlp
import configManager as cfm
import app_config


def enable_dpi_awareness():
    """Make the process DPI-aware on Windows so Tk widgets scale more predictably."""
    if sys.platform != "win32":
        return
    
    import ctypes
    try:
        # Windows 8.1+ API
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            # Older fallback
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

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
        updYtdlpBtn (ttk.Button): The button to update yt-dlp.
        console_scrollbar (ttk.Scrollbar): The scrollbar for the console output.
        console_output (tk.Text): The text widget for the console output.
    """
    def __init__(self) -> None:
        enable_dpi_awareness()

        self.version = "1.0.0"
        self.root = tk.Tk()
        self.root.title(f"yt-dlp Simplified {self.version}")


        self.root.geometry('600x600')

        self.root.resizable(False, False)
        self.root.minsize(460, 300)


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


        ttk.Label(container, text="Enter URL:").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.urlEntry = ttk.Entry(container)
        self.urlEntry.grid(row=0, column=1, sticky="ew", pady=(0, 8))
        self.urlEntry.focus()
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
        self.browseBtn.grid(row=1, column=0, sticky="w")

        self.locationEntry = ttk.Entry(container, state="disabled")
        self.locationEntry.grid(row=1, column=1, sticky="ew")
        self.updLocEntry(dat) # type: ignore


        self.audOnly = tk.BooleanVar(value=False)
        self.audOnlyBtn = ttk.Checkbutton(container, text="Audio only", variable=self.audOnly)
        self.audOnlyBtn.grid(row=2, column=0, sticky="w", pady=(8, 0))


        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=2, column=1, sticky="e", pady=(8, 0))

        self.dwnBtn = ttk.Button(btn_frame, text="Download", command=self.download)
        self.dwnBtn.pack(side="right")

        self.updYtdlpBtn = ttk.Button(btn_frame, text="Update yt-dlp", command=self.updDlp)
        self.updYtdlpBtn.pack(side="right", padx=(6, 0))


        console_frame = ttk.Frame(container)
        console_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        console_frame.columnconfigure(0, weight=1) # Make text widget expand
        console_frame.rowconfigure(0, weight=1)    # Make text widget expand

        self.console_scrollbar = ttk.Scrollbar(console_frame, orient="vertical")
        self.console_output = tk.Text(
            console_frame,
            wrap="word",
            state="disabled",
            yscrollcommand=self.console_scrollbar.set,
            height=5
        )
        self.console_scrollbar.config(command=self.console_output.yview)


        self.console_output.grid(row=0, column=0, sticky="nsew")
        self.console_scrollbar.grid(row=0, column=1, sticky="ns")

        self.append_to_console(f"yt-dlp Simplified {self.version}\nNot intended for any unethical purpose. (github.com/aymanibnezakir)\n")
        

        self.run_startup_checks()


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
        
        self.root.after(0, _append)

    def disable_buttons(self):
        """Disables buttons during an operation."""
        self.dwnBtn.config(state="disabled")
        self.updYtdlpBtn.config(state="disabled")

    def enable_buttons(self):
        """Enables buttons after an operation."""
        self.dwnBtn.config(state="normal")
        self.updYtdlpBtn.config(state="normal")
    
    
    def run_startup_checks(self):
        """Runs dependency checks and initial update check."""
        self.append_to_console("Executing file check...")
        
        problems = app_config.check_dependencies()
        
        if not problems:
            self.append_to_console("Dependencies found. Standby...")
            
        else:
            for item in problems:
                self.append_to_console(f"Error: {item}")
            self.append_to_console("Error: Add missing files to the bins folder or fix permissions.")
            self.disable_buttons() 
            self.append_to_console("All operations disabled until dependencies are fixed.")


    def updDlp(self):
        update_handler = update_ytdlp.Update()       
        self.disable_buttons()
        self.append_to_console("Initializing yt-dlp update...")
        
        threading.Thread(
            target=self.run_update_thread, 
            args=(update_handler,), 
            daemon=True
        ).start()

    
    def run_update_thread(self, update_handler: update_ytdlp.Update):
        """Worker thread for running the update process."""
        try:
            update_handler.update(self.append_to_console)
            self.append_to_console("Update check finished.")
        except Exception as e:
            self.append_to_console(f"Update failed: {e}")
        finally:
            self.root.after(0, self.enable_buttons)

    
    def download(self):
        url = self.urlEntry.get().strip()
        save_path = self.locationEntry.get().strip() 
        aud_only = self.audOnly.get()

        # --- Validation ---
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            return

        if not save_path:
            messagebox.showerror("Error", "Please choose a save location (directory).")
            return
        
        # Use a temporary handler just for validation
        validator = download_module.Download(url, aud_only, save_path)
        if not validator.verifyLink():
            messagebox.showerror("Error", "Invalid URL provided.")
            return
        
        # --- Start Download Thread ---
        self.disable_buttons()
        self.append_to_console(f"Starting download for: {url}")
        
        # Create the real handler for the thread
        download_handler = download_module.Download(url, aud_only, save_path)
        
        threading.Thread(
            target=self.run_download_thread, 
            args=(download_handler,), 
            daemon=True
        ).start()

    
    def run_download_thread(self, download_handler: download_module.Download):
        """Worker thread for running the download process."""
        try:
            # Pass the console append method as a callback
            download_handler.run_download(self.append_to_console)
        except Exception as e:
            self.append_to_console(f"Download failed: {e}")
        finally:
            # Re-enable buttons back on the main thread
            self.root.after(0, self.enable_buttons)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    window = Window()
    window.run()