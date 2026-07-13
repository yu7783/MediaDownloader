import subprocess
import threading
import time
import pyperclip
import sys
import os

class ClipboardMonitor(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.running = True
        self.daemon = True
        self.last_text = pyperclip.paste()

    def run(self):
        while self.running:
            try:
                current_text = pyperclip.paste()
                if current_text != self.last_text:
                    self.last_text = current_text
                    if current_text.startswith('http://') or current_text.startswith('https://'):
                        self.callback(current_text)
            except Exception:
                pass
            time.sleep(1)

    def stop(self):
        self.running = False

def check_for_updates(callback):
    """Checks for yt-dlp updates using its built-in -U flag"""
    def _update():
        try:
            callback("アップデートを確認中...")
            # We'll try to run yt-dlp -U
            if getattr(sys, 'frozen', False):
                # If packaged
                cmd = ['yt-dlp', '-U']
            else:
                cmd = [sys.executable, '-m', 'yt_dlp', '-U']
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            output, _ = process.communicate()
            if "up to date" in output.lower():
                callback("yt-dlpは最新版です。")
            else:
                callback("yt-dlpをアップデートしました。")
        except Exception as e:
            callback(f"アップデート確認エラー: {e}")
            
    threading.Thread(target=_update, daemon=True).start()
