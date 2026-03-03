"""
Windows Startup mein AI Employee (all processes via PM2) add karo
Run karo: python setup_autostart.py
"""

import os
import shutil

# Project root ke start_all.bat ko point karo (3 processes: master-pipeline, whatsapp-watcher, linkedin-poster)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
BATCH_FILE = os.path.join(PROJECT_ROOT, 'start_all.bat')
STARTUP_FOLDER = os.path.join(
    os.environ['APPDATA'],
    'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
)
SHORTCUT_NAME = 'AI_Employee_Pipeline.bat'
DEST = os.path.join(STARTUP_FOLDER, SHORTCUT_NAME)


def main():
    print("=" * 45)
    print("  AI Employee — Windows Auto-Start Setup")
    print("=" * 45)

    if not os.path.exists(BATCH_FILE):
        print(f"[ERROR] Batch file nahi mila: {BATCH_FILE}")
        print(f"[INFO]  Expected: {BATCH_FILE}")
        return

    print(f"[OK] Batch file found: {BATCH_FILE}")
    print(f"[..] Startup folder: {STARTUP_FOLDER}")

    # Copy to startup folder
    shutil.copy2(BATCH_FILE, DEST)
    print(f"[OK] Copied to startup: {DEST}")

    print()
    print("=" * 45)
    print("  Setup Complete!")
    print("  PC restart hone par sab 3 processes")
    print("  (PM2 via start_all.bat) auto-start honge.")
    print("=" * 45)


if __name__ == '__main__':
    main()
