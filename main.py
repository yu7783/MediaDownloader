import sys
import os
import glob

def load_patches():
    # exeの同じ階層にある patches フォルダからパッチを読み込む
    base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    patch_dir = os.path.join(base_dir, 'patches')
    
    if os.path.exists(patch_dir):
        sys.path.insert(0, patch_dir)
        for patch_file in glob.glob(os.path.join(patch_dir, '*.py')):
            if not patch_file.endswith('__init__.py'):
                module_name = os.path.basename(patch_file)[:-3]
                try:
                    __import__(module_name)
                    print(f"Loaded patch: {module_name}")
                except Exception as e:
                    print(f"Failed to load patch {module_name}: {e}")

# パッチのロード（メインロジックのインポート前に実行）
load_patches()

from gui import App

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
