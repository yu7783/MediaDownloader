# Universal Video Downloader パッチ作成仕様書

本アプリケーション（`UniversalVideoDownloader.exe`）は、**再ビルドを行うことなく、Pythonスクリプトを追加するだけで後から機能を上書き・追加（ホットパッチ）できる**仕組みを備えています。

このドキュメントでは、パッチの作成方法と仕様について解説します。

---

## 1. パッチの基本仕様

- **パッチの配置場所**: `.exe` と同じ階層にある `patches` フォルダ内
- **ファイル形式**: 任意の名前のPythonファイル（例: `my_patch.py`）
- **読み込みタイミング**: アプリケーション（GUI）が初期化される**直前**に、`patches` フォルダ内のすべての `.py` ファイル（`__init__.py` を除く）が自動的に `import` されます。

> [!TIP]
> 読み込まれたスクリプト内で、元のクラスのメソッドを上書き（モンキーパッチ）することで、GUIの挙動やダウンロードロジックを変更できます。

---

## 2. モンキーパッチの基本構造

Pythonの動的な性質を利用して、既存のクラスメソッドを自分が定義した新しい関数にすり替えます。

### サンプル: アプリ起動時のタイトルを変更するパッチ

`patches/change_title.py` として以下を保存するだけで、アプリのタイトルが変わります。

```python
# patches/change_title.py
import gui

# 元のメソッドを退避（必要に応じて呼び出すため）
original_init = gui.App.__init__

def new_init(self):
    # 元の初期化処理を実行
    original_init(self)
    
    # あとからタイトルを上書き
    self.title("My Custom Video Downloader - Patched!")

# クラスのメソッドを新しい関数ですり替え（モンキーパッチ）
gui.App.__init__ = new_init
```

---

## 3. 実践的なパッチ例

### 例1: yt-dlpのオプションを強制的に追加・変更する
ダウンロード処理（`downloader.py`）内のオプション生成メソッドをフックして、独自のオプションを挿入します。

```python
# patches/custom_ytdlp_opts.py
import downloader

original_get_base_options = downloader.Downloader.get_base_options

def patched_get_base_options(self, video_q, audio_q, ext, use_cookie=None):
    # まず元のメソッドを呼び出して基本設定を取得
    opts = original_get_base_options(self, video_q, audio_q, ext, use_cookie)
    
    # 独自のオプションを追加 (例: プロキシを経由させる)
    opts['proxy'] = 'http://127.0.0.1:8080'
    
    # 特定のサイトの抽出制限を回避するためのオプションを追加
    opts['sleep_requests'] = 2.0 
    
    return opts

downloader.Downloader.get_base_options = patched_get_base_options
```

### 例2: GUIに新しいボタンを強引に追加する
UIコンポーネント（`gui.py`）の初期化処理に割り込み、サイドバーなどに新しいボタンを追加します。

```python
# patches/add_custom_button.py
import gui
import customtkinter as ctk
import webbrowser

original_init = gui.App.__init__

def new_init(self):
    original_init(self)
    
    # サイドバーの一番下に新しいボタンを追加
    def open_help():
        webbrowser.open("https://github.com/yt-dlp/yt-dlp")
        
    self.help_button = ctk.CTkButton(self.sidebar_frame, text="ヘルプ(yt-dlp)", command=open_help)
    self.help_button.grid(row=5, column=0, padx=20, pady=10)

gui.App.__init__ = new_init
```

---

## 4. パッチ開発時の注意点

> [!WARNING]
> - パッチファイルはアルファベット順（OSの `glob` 取得順）に実行されます。依存関係がある場合はファイル名の先頭に `01_xxx.py` のように番号をつけて制御してください。
> - エラーが発生したパッチはスキップされます。パッチ内のエラーによってアプリ全体が起動しなくなるのを防ぐため、内部で `try-except` で保護されています。
> - Python標準ライブラリや `yt_dlp` などの依存モジュールへのパッチも、このファイル内から直接 `import yt_dlp` として上書き可能です。
