# Universal Video Downloader Patch Creation Specification

This application (`UniversalVideoDownloader.exe`) features a mechanism that allows you to dynamically override or add functionality (hot-patching) on the fly simply by adding Python scripts, **without requiring a rebuild**.

This document explains the specifications and procedures for creating patches.

This English specification document was created using machine translation. Please note that there may be some errors.

---

## 1. Basic Patch Specifications

- **Patch Location**: Inside the `patches` folder located in the same directory as the `.exe`.
- **File Format**: Python files with arbitrary names (e.g., `my_patch.py`).
- **Loading Timing**: All `.py` files (excluding `__init__.py`) within the `patches` folder are automatically imported **immediately before** the application (GUI) initializes.

> [!TIP]
> You can modify GUI behavior or download logic by overriding (monkey-patching) methods of the original classes within the loaded scripts.

---

## 2. Basic Structure of Monkey Patching

By leveraging Python's dynamic nature, you can swap existing class methods with new functions you define yourself.

### Sample: Patch to Change the App Title at Startup

Simply saving the following code as `patches/change_title.py` will change the application's title.

```python
# patches/change_title.py
import gui

# Save the original method (to call it if necessary)
original_init = gui.App.__init__

def new_init(self):
    # Execute the original initialization process
    original_init(self)

    # Overwrite the title
    self.title("My Custom Video Downloader - Patched!")

# Replace the class method with the new function (monkey patching)
gui.App.__init__ = new_init

```

---

## 3. Practical Patch Examples

### Example 1: Modifying yt-dlp Options Dynamically

Hook the option generation method within the download process (`downloader.py`) to insert custom options.

```python
# patches/custom_ytdlp_opts.py
import downloader

original_get_base_options = downloader.Downloader.get_base_options

def patched_get_base_options(self, video_q, audio_q, ext, use_cookie=None):
    # First, call the original method to get the base settings
    opts = original_get_base_options(self, video_q, audio_q, ext, use_cookie)

    # Add custom options (e.g., routing through a proxy)
    opts['proxy'] = 'http://127.0.0.1:8080'
    # Add a delay between requests to avoid rate limits on specific sites
    opts['sleep_requests'] = 2.0

    return opts

downloader.Downloader.get_base_options = patched_get_base_options

```

### Example 2: Adding a Custom Button to the GUI

Intercept the initialization process of the UI component (`gui.py`) to add a new button to the sidebar.

```python
# patches/add_custom_button.py
import gui
import customtkinter as ctk
import webbrowser

original_init = gui.App.__init__

def new_init(self):
    original_init(self)

    # Add a new button at the bottom of the sidebar
    def open_help():
        webbrowser.open("https://github.com/yt-dlp/yt-dlp")

    self.help_button = ctk.CTkButton(self.sidebar_frame, text="Help (yt-dlp)", command=open_help)
    self.help_button.grid(row=5, column=0, padx=20, pady=10)

gui.App.__init__ = new_init

```

---

## 4. Points to Note When Developing Patches

> [!WARNING]
> * Patch files are executed in alphabetical order (based on the OS's `glob` retrieval order). If there are dependencies, manage the execution order by prefixing filenames with numbers, such as `01_xxx.py`.
> * Patches that encounter errors are skipped. Internal `try-except` blocks prevent errors within a single patch from blocking the entire application startup.
> * You can also directly overwrite other modules—including Python standard libraries or external dependencies like `yt_dlp`—by importing them within your patch file.
