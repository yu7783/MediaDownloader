import customtkinter as ctk
from downloader import Downloader
from utils import check_for_updates, ClipboardMonitor
from database import init_db, get_history
import threading

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance settings
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title("Universal Video Downloader")
        self.geometry("800x600")
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize DB
        init_db()

        self.standby_mode = False

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Downloader", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.home_button = ctk.CTkButton(self.sidebar_frame, text="ホーム", command=self.show_home)
        self.home_button.grid(row=1, column=0, padx=20, pady=10)

        self.history_button = ctk.CTkButton(self.sidebar_frame, text="履歴", command=self.show_history)
        self.history_button.grid(row=2, column=0, padx=20, pady=10)

        self.update_button = ctk.CTkButton(self.sidebar_frame, text="更新確認", command=self.check_updates)
        self.update_button.grid(row=3, column=0, padx=20, pady=10)

        # Main Home Frame
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)
        
        self.url_entry = ctk.CTkEntry(self.home_frame, placeholder_text="動画のURLをペーストしてください...")
        self.url_entry.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Options Frame for comboboxes
        self.options_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        self.options_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.options_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.video_quality_var = ctk.StringVar(value="最高画質")
        self.video_quality_combo = ctk.CTkComboBox(self.options_frame, values=["最高画質", "1080p", "720p", "360p"], variable=self.video_quality_var)
        self.video_quality_combo.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.audio_quality_var = ctk.StringVar(value="最高音質")
        self.audio_quality_combo = ctk.CTkComboBox(self.options_frame, values=["最高音質", "320kbps", "256kbps", "128kbps"], variable=self.audio_quality_var)
        self.audio_quality_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.ext_var = ctk.StringVar(value="mp4")
        self.ext_combo = ctk.CTkComboBox(self.options_frame, values=["mp3", "mp4", "flac", "wav", "mka", "mkv"], variable=self.ext_var)
        self.ext_combo.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Button Frame
        self.button_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.download_button = ctk.CTkButton(self.button_frame, text="ダウンロード開始", command=self.start_download)
        self.download_button.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.standby_button = ctk.CTkButton(self.button_frame, text="待機モード: OFF", command=self.toggle_standby, fg_color="gray")
        self.standby_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(self.home_frame)
        self.progress_bar.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.home_frame, text="待機中...")
        self.status_label.grid(row=4, column=0, padx=20, pady=10)

        self.log_textbox = ctk.CTkTextbox(self.home_frame, height=200)
        self.log_textbox.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.home_frame.grid_rowconfigure(5, weight=1)

        # History Frame
        self.history_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(0, weight=1)
        
        self.history_textbox = ctk.CTkTextbox(self.history_frame)
        self.history_textbox.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Initialize downloader
        self.downloader = Downloader(
            progress_callback=self.update_progress,
            log_callback=self.add_log,
            finished_callback=self.download_finished
        )

        # Clipboard Monitor
        self.clipboard_monitor = ClipboardMonitor(self.on_clipboard_change)
        self.clipboard_monitor.start()

        # Show Home by default
        self.show_home()

    def show_home(self):
        self.history_frame.grid_forget()
        self.home_frame.grid(row=0, column=1, sticky="nsew")

    def show_history(self):
        self.home_frame.grid_forget()
        self.history_frame.grid(row=0, column=1, sticky="nsew")
        self.load_history()

    def load_history(self):
        self.history_textbox.delete("1.0", "end")
        rows = get_history()
        for row in rows:
            self.history_textbox.insert("end", f"[{row[3]}] {row[2]}\n状態: {row[0]} - {row[1]}\n\n")

    def on_clipboard_change(self, text):
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, text)
        self.add_log("クリップボードからURLを自動入力しました。")
        if self.standby_mode:
            if self.download_button.cget("state") != "disabled":
                self.add_log("待機モードONのため、自動ダウンロードを開始します。")
                self.start_download()
            else:
                self.add_log("現在ダウンロード中のため、自動開始をスキップしました。")

    def toggle_standby(self):
        self.standby_mode = not self.standby_mode
        if self.standby_mode:
            self.standby_button.configure(text="待機モード: ON (全自動)", fg_color="#d9534f", text_color="white", font=ctk.CTkFont(weight="bold"))
            self.add_log("待機モードをONにしました。URLをコピーするだけで自動ダウンロードが開始されます。")
        else:
            self.standby_button.configure(text="待機モード: OFF", fg_color="gray", text_color="white", font=ctk.CTkFont(weight="normal"))
            self.add_log("待機モードをOFFにしました。")

    def check_updates(self):
        self.add_log("yt-dlpのアップデートを確認中...")
        check_for_updates(self.add_log)

    def add_log(self, message):
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")

    def update_progress(self, percent, speed_str):
        self.progress_bar.set(percent / 100)
        self.status_label.configure(text=f"進捗: {percent:.1f}% - 速度: {speed_str}")

    def download_finished(self, success):
        if success:
            self.status_label.configure(text="完了しました。")
            self.progress_bar.set(1.0)
        else:
            self.status_label.configure(text="失敗しました。")
            self.progress_bar.set(0.0)
        self.download_button.configure(state="normal")

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            self.add_log("URLを入力してください。")
            return
        
        video_q = self.video_quality_var.get()
        audio_q = self.audio_quality_var.get()
        ext = self.ext_var.get()
        
        self.download_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="準備中...")
        self.log_textbox.delete("1.0", "end")
        self.downloader.start_download(url, video_q, audio_q, ext)

    def on_closing(self):
        self.clipboard_monitor.stop()
        self.destroy()
