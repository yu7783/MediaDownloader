import subprocess
import threading
import time
import pyperclip
import sys
import os
import shutil
import urllib.request
import json
import tkinter.messagebox


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

def check_and_install_dependencies(parent=None):
    dependencies = {
        'yt-dlp': 'yt-dlp.yt-dlp',
        'ffmpeg': 'Gyan.FFmpeg',
        'aria2c': 'aria2.aria2'
    }
    missing = []
    for cmd in dependencies.keys():
        if shutil.which(cmd) is None:
            missing.append(cmd)
            
    if missing:
        msg = f"以下の必須コンポーネントがインストールされていません：\n{', '.join(missing)}\n\nwingetを使用して自動的にダウンロード・インストールしますか？\n(※コマンドプロンプトが開きインストール処理が行われます)"
        if tkinter.messagebox.askyesno("必須コンポーネントの確認", msg, parent=parent):
            for cmd in missing:
                pkg_id = dependencies[cmd]
                try:
                    subprocess.run(['winget', 'install', '--id', pkg_id, '-e', '--source', 'winget', '--accept-package-agreements', '--accept-source-agreements'], 
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
                except Exception as e:
                    tkinter.messagebox.showerror("インストール失敗", f"{cmd} のインストールに失敗しました: {e}", parent=parent)

APP_VERSION = "v1.1.0"

def parse_version(v_str):
    try:
        return tuple(map(int, v_str.strip('v').split('.')))
    except:
        return (0, 0, 0)

def download_github_patches(parent=None):
    url = "https://api.github.com/repos/yu7783/MediaDownloader/releases"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            releases = json.loads(response.read().decode())
            
            base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
            patch_dir = os.path.join(base_dir, 'patches')
            os.makedirs(patch_dir, exist_ok=True)
            
            current_v = parse_version(APP_VERSION)
            
            # 古いバージョンから順に処理
            releases.sort(key=lambda r: parse_version(r.get('tag_name', 'v0.0.0')))
            
            downloaded = False
            latest_found = None
            
            for release in releases:
                tag_name = release.get('tag_name', '')
                rel_v = parse_version(tag_name)
                
                # 現在のバージョンより新しいリリースをすべて処理（経由する）
                if rel_v > current_v:
                    assets = release.get('assets', [])
                    for asset in assets:
                        filename = asset['name']
                        if filename.endswith('.py') and filename != 'update_patch.py':
                            download_url = asset['browser_download_url']
                            file_path = os.path.join(patch_dir, filename)
                            
                            if not os.path.exists(file_path):
                                req_dl = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
                                with urllib.request.urlopen(req_dl) as dl_resp:
                                    content = dl_resp.read()
                                    with open(file_path, 'wb') as f:
                                        f.write(content)
                                downloaded = True
                                latest_found = tag_name
                                
            if downloaded and parent and latest_found:
                parent.after(0, lambda: tkinter.messagebox.showinfo(
                    "アップデート", f"新しいバージョン ({latest_found}) までの差分パッチを順次ダウンロードしました。\n次回起動時から適用されます。", parent=parent))
                    
    except Exception as e:
        print(f"Patch download error: {e}")
