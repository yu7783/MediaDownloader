# Universal Video Downloader User Manual & Specifications

This English specification document was created using machine translation.
Please note that there may be some errors.

This application is a high-performance video downloader designed for maximum speed and convenience, utilizing yt-dlp, aria2c, and ffmpeg.

---

## 🌟 Key Features and Capabilities

### 1. Ultra-Fast Downloading (Optimized Specifications)
- **aria2c Integration**: Establishes up to 32 connections per file (`-x 32 -s 32 -j 32`) for blazing-fast download speeds.
- **Parallel Fragment Downloading**: Supports yt-dlp's parallel fragment downloading (32 concurrent streams), accelerating downloads for HLS and DASH-streamed videos.
- **ffmpeg Multi-threaded Processing**: Automatically detects your PC's CPU core count and fully utilizes multi-threading (`-threads N`) for video/audio merging and encoding tasks.
- **SSD Optimization**: Uses the aria2c `--file-allocation=none` option to skip unnecessary disk allocation delays at the start of downloads, thereby preserving SSD lifespan and maintaining high speeds.

### 2. Extensive Site Support and Bypass Capabilities
- **Supported Sites**: YouTube, TikTok, Niconico, X (Twitter), SoundCloud, Bilibili, Twitch, Instagram, etc. (compatible with thousands of sites supported by yt-dlp).
- **Full Support for Shorts & Live Stream Archives**
- **YouTube "403 Forbidden" Bypass**: To circumvent the latest restrictions, the app internally spoofs a smartphone (iOS) client when attempting downloads.
- **Fully Automated Cookie Switching**:
1. First, it attempts a safe download without using cookies. 
2. If that fails, it automatically loads cookies from your PC's browsers in a specific order (`Chrome` → `Edge` → `Firefox` → `Brave`) and retries the download for age-restricted or member-only videos. ### 3. Smart UI and Fully Automated Features (Standby Mode)
- **Japanese UI with Dark Mode**: A stylish GUI built with CustomTkinter that is easy on the eyes.
- **Automatic Clipboard Monitoring**: Simply "copy" a video URL in your browser, and it is automatically pasted into the app's input field.
- **Standby Mode (Fully Automated Download)**: When "Standby Mode" is enabled, downloading starts **automatically without a single click** the moment you copy a URL. This is the ultimate feature for saving multiple videos in succession.

### 4. Extension and Maintenance Features
- **Download History**: Past download history is recorded in an SQLite database and can be viewed at any time via the "History" tab.
- **Automatic Updates**: Update the core download engine (`yt-dlp`) to the latest version with a single click using the "Check for Updates" button. (This allows you to quickly fix download failures caused by changes to video site specifications.)
- **Hot-Patching Capability**: Even after converting the app to an executable (`.exe`), you can apply community-created patches or add new features simply by placing Python scripts in the `patches` folder.

---

## 🛠️ Prerequisites (Required Environment)

This software utilizes the following powerful external tools internally. You must install them beforehand and add them to your system's **Environment Variables (PATH)**.

1. **ffmpeg**: Essential for merging video and audio and for format conversion.
2. **aria2c**: The engine used for ultra-fast, 32-stream parallel downloading.

---

## 📖 How to Use

### Basic Downloading
1. Launch the software (`UniversalVideoDownloader.exe` or `python main.py`).
2. Copy the URL of the video you wish to download (it will automatically appear in the input field). 3. Select your preferred settings from the dropdown menus below the input field:
- **Video Quality**: Highest Quality / 1080p / 720p / 360p
- **Audio Quality**: Highest Quality / 320kbps / 256kbps / 128kbps (Valid only when extracting audio)
- **File Extension**: mp4 / mkv (for video) or mp3 / flac / wav / mka (for audio)
4. Click **"Start Download"**.

### How to use Standby Mode
Click "Standby Mode: OFF" next to the "Start Download" button to turn it ON (it will turn red).
In this mode, simply "Copy Link" in your browser or the X (Twitter) app, and downloads will proceed automatically in the background using your specified quality and format.
> *Note: If you copy a new URL while a download is in progress, the automatic start will be skipped for safety reasons.

### Troubleshooting Errors
If an error appears in the log screen, please try the following:
- **Click the "Check for Updates" button**: Updating yt-dlp to the latest version resolves the issue in 90% of cases.
- **Close your browser**: If cookie loading fails (e.g., with members-only videos), completely close the browser (such as Chrome) before downloading; this releases the cookie lock and allows the download to succeed.

---

## Patching Feature
This software supports applying patches after the build process.
For details, please see [here](PATCH_GUIDE_ENG.md).
