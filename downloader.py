import yt_dlp
import multiprocessing
import threading
from database import add_download
import traceback
import re

class Downloader:
    def __init__(self, progress_callback, log_callback, finished_callback):
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.finished_callback = finished_callback
        self.browsers = ['chrome', 'edge', 'firefox', 'brave']
        self.cpu_count = multiprocessing.cpu_count()
        self.cancel_flag = False

    def get_base_options(self, video_q, audio_q, ext, use_cookie=None):
        ydl_opts = {
            'merge_output_format': 'mkv',
            'concurrent_fragment_downloads': 32,
            'noprogress': True,
            'quiet': True,
            'no_warnings': True,
            'logger': MyLogger(self.log_callback),
            'progress_hooks': [self.my_hook],
            'outtmpl': '%(title)s.%(ext)s',
            'extractor_args': {'youtube': ['player_client=ios,web']},
            # ffmpeg multi-threading
            'postprocessor_args': [
                '-threads', str(self.cpu_count)
            ],
            # External downloader aria2c parameters (32 connections)
            'external_downloader': 'aria2c',
            'external_downloader_args': ['-x', '32', '-s', '32', '-j', '32', '-k', '1M', '--file-allocation=none'],
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10
        }
        
        audio_exts = ['mp3', 'flac', 'wav', 'mka']
        if ext in audio_exts:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['extract_audio'] = True
            ydl_opts['audio_format'] = ext
            
            if audio_q == "最高音質":
                ydl_opts['audio_quality'] = '0'
            elif audio_q == "320kbps":
                ydl_opts['audio_quality'] = '320K'
            elif audio_q == "256kbps":
                ydl_opts['audio_quality'] = '256K'
            elif audio_q == "128kbps":
                ydl_opts['audio_quality'] = '128K'
        else:
            if video_q == "最高画質":
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            elif video_q == "1080p":
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
            elif video_q == "720p":
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
            elif video_q == "360p":
                ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
                
            ydl_opts['merge_output_format'] = ext

        if use_cookie:
            ydl_opts['cookiesfrombrowser'] = (use_cookie, )
            
        return ydl_opts

    def my_hook(self, d):
        if self.cancel_flag:
            raise Exception("Canceled by user")
            
        if d['status'] == 'downloading':
            try:
                # Calculate progress
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                if total > 0:
                    percent = (downloaded / total) * 100
                else:
                    percent = 0
                
                speed = d.get('speed', 0)
                if speed:
                    speed_str = f"{speed / 1024 / 1024:.2f} MB/s"
                else:
                    speed_str = "Unknown"
                    
                self.progress_callback(percent, speed_str)
            except Exception:
                pass
        elif d['status'] == 'finished':
            self.progress_callback(100, "処理中...")

    def start_download(self, url, video_q, audio_q, ext):
        self.cancel_flag = False
        threading.Thread(target=self._download_thread, args=(url, video_q, audio_q, ext), daemon=True).start()

    def _download_thread(self, url, video_q, audio_q, ext):
        self.log_callback(f"ダウンロード開始: {url}")
        
        success = False
        final_error = None
        title = url
        
        # Try without cookie first
        self.log_callback("Cookieなしで試行中...")
        opts = self.get_base_options(video_q, audio_q, ext, use_cookie=None)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and 'title' in info:
                    title = info['title']
                ydl.download([url])
                success = True
        except Exception as e:
            self.log_callback(f"Cookieなしでの試行に失敗しました: {e}")
            final_error = e

        # Iterate over browsers if failed
        if not success:
            for browser in self.browsers:
                if self.cancel_flag:
                    break
                self.log_callback(f"Cookieを使用して再試行中: {browser}...")
                opts = self.get_base_options(video_q, audio_q, ext, use_cookie=browser)
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        if info and 'title' in info:
                            title = info['title']
                        ydl.download([url])
                        success = True
                        break
                except Exception as e:
                    self.log_callback(f"{browser} での試行に失敗しました: {e}")
                    final_error = e

        if success:
            self.log_callback(f"ダウンロード完了: {title}")
            add_download(title, url, "完了")
            self.finished_callback(True)
        else:
            self.log_callback(f"全ての試行に失敗しました。")
            add_download(title, url, "失敗")
            self.finished_callback(False)

class MyLogger:
    def __init__(self, callback):
        self.callback = callback
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
    def _clean(self, msg):
        return self.ansi_escape.sub('', msg)
        
    def debug(self, msg):
        pass
    def warning(self, msg):
        self.callback(f"警告: {self._clean(msg)}")
    def error(self, msg):
        self.callback(f"エラー: {self._clean(msg)}")
