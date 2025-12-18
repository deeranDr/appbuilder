# updater_client.py
import os
import sys
import json
import time
import tempfile
import subprocess
import hashlib
import platform
import requests
import tkinter as tk
from tkinter import messagebox

# 🔹 Hosted version file
VERSION_URL = "https://vmg-premedia-22112023.s3.ap-southeast-2.amazonaws.com/application/drn/latest_version.json"

def sha256(path):
    """Compute lowercase SHA256 checksum."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest().lower()

def ask_user_to_update(latest):
    """Ask user if they want to update."""
    root = tk.Tk()
    root.withdraw()
    res = messagebox.askyesno(
        "Update Available",
        f"A new version {latest} is available.\nDo you want to update now?"
    )
    root.destroy()
    return res

def check_for_update(current_version, exe_path):
    """Check S3 JSON for update and apply if needed."""
    try:
        r = requests.get(f"{VERSION_URL}?t={int(time.time())}", timeout=8)
        data = r.json()
        latest_version = data.get("version", "").strip()
        if not latest_version:
            print("[Updater] ❌ Invalid version JSON.")
            return

        print(f"[Updater] Current: {current_version} | Latest: {latest_version}")
        if latest_version == current_version:
            print("[Updater] ✅ Already up to date.")
            return

        mandatory = bool(data.get("mandatory"))
        if not mandatory and not ask_user_to_update(latest_version):
            print("[Updater] Skipped by user.")
            return

        os_type = platform.system()

        if os_type == "Windows":
            platform_data = data.get("windows", {})
        elif os_type == "Darwin":
            platform_data = data.get("mac", {})
        else:
            messagebox.showerror("Update Error", f"Unsupported OS: {os_type}")
            return

        download_url = platform_data.get("url")
        expected_sha = platform_data.get("sha256", "").lower()

        if not download_url or not expected_sha:
            messagebox.showerror(
                "Update Error",
                "Invalid update metadata for this platform."
            )
            return



        # 🔹 Download new EXE
        tmp_file = os.path.join(tempfile.gettempdir(), os.path.basename(download_url))
        print(f"[Updater] Downloading from {download_url} ...")
        with requests.get(download_url, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            with open(tmp_file, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"[Updater] Downloaded to: {tmp_file}")



        # 🔹 Verify checksum
        expected = data.get("sha256", "").strip().lower()
        actual = sha256(tmp_file)
        if expected and actual != expected:
            messagebox.showerror("Checksum Error", "Downloaded file failed verification.")
            os.remove(tmp_file)
            return

        # 🔹 Launch updater
        if os_type == "Windows":
            updater_path = os.path.join(os.path.dirname(exe_path), "updater.exe")
            if not os.path.exists(updater_path):
                messagebox.showerror("Update Error", f"Missing updater.exe at:\n{updater_path}")
                return

            print(f"[Updater] Launching updater: {updater_path}")
            subprocess.Popen([updater_path, tmp_file, exe_path], shell=False)

            # wait a little before exit so file lock clears
            time.sleep(2)
            sys.exit(0)

        elif os_type == "Darwin":
            updater_path = os.path.join(os.path.dirname(exe_path), "updater.sh")

            if not os.path.exists(updater_path):
                messagebox.showerror("Update Error", "Missing updater.sh")
                return

            subprocess.Popen(["bash", updater_path, tmp_file])
            sys.exit(0)


    except Exception as e:
        print(f"[Updater] ❌ Update failed: {e}")


# updater_client.py
# updater_client.py
# import os
# import sys
# import time
# import json
# import tempfile
# import subprocess
# import hashlib
# import platform
# import requests

# from PySide6.QtWidgets import QMessageBox, QApplication
# from PySide6.QtCore import Qt

# # 🔹 Hosted version file
# VERSION_URL = (
#     "https://vmg-premedia-22112023.s3.ap-southeast-2.amazonaws.com/"
#     "application/drn/latest_version.json"
# )

# # --------------------------------------------------
# # Utilities
# # --------------------------------------------------

# def sha256(path: str) -> str:
#     """Compute lowercase SHA256 checksum."""
#     h = hashlib.sha256()
#     with open(path, "rb") as f:
#         for chunk in iter(lambda: f.read(8192), b""):
#             h.update(chunk)
#     return h.hexdigest().lower()


# def _ensure_qt_app():
#     """Ensure QApplication exists (safe for timers/background calls)."""
#     if QApplication.instance() is None:
#         QApplication(sys.argv)


# def show_error(title: str, message: str):
#     _ensure_qt_app()
#     msg = QMessageBox()
#     msg.setWindowTitle(title)
#     msg.setText(message)
#     msg.setIcon(QMessageBox.Critical)
#     msg.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
#     msg.exec()


# def ask_user_to_update(latest_version: str) -> bool:
#     """
#     PySide6-only update dialog
#     YES button only (no cancel)
#     """
#     _ensure_qt_app()

#     msg = QMessageBox()
#     msg.setWindowTitle("Update Available")
#     msg.setText(f"A new version {latest_version} is available.")
#     msg.setInformativeText("Click YES to update now.")
#     msg.setIcon(QMessageBox.Information)

#     yes_btn = msg.addButton("Yes", QMessageBox.AcceptRole)
#     msg.setDefaultButton(yes_btn)

#     msg.setWindowFlags(
#         Qt.Dialog |
#         Qt.WindowStaysOnTopHint |
#         Qt.CustomizeWindowHint |
#         Qt.WindowTitleHint
#     )

#     msg.exec()
#     return True


# # --------------------------------------------------
# # Update state (prevent popup spam)
# # --------------------------------------------------

# def _get_update_state_file():
#     if platform.system() == "Windows":
#         base = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
#         return os.path.join(base, "PremediaApp", "update_state.json")
#     else:
#         return os.path.join(
#             os.path.expanduser("~"),
#             ".premediaapp",
#             "update_state.json"
#         )


# def _load_update_state():
#     path = _get_update_state_file()
#     try:
#         if os.path.exists(path):
#             with open(path, "r") as f:
#                 return json.load(f)
#     except Exception:
#         pass
#     return {}


# def _save_update_state(state: dict):
#     path = _get_update_state_file()
#     os.makedirs(os.path.dirname(path), exist_ok=True)
#     with open(path, "w") as f:
#         json.dump(state, f)


# # --------------------------------------------------
# # Main update logic
# # --------------------------------------------------

# def check_for_update(current_version: str, exe_path: str):
#     """Check S3 JSON for update and apply if needed."""
#     try:
#         # Fetch version JSON
#         r = requests.get(f"{VERSION_URL}?t={int(time.time())}", timeout=8)
#         r.raise_for_status()
#         data = r.json()

#         latest_version = str(data.get("version", "")).strip()
#         if not latest_version:
#             print("[Updater] ❌ Invalid version JSON.")
#             return

#         print(f"[Updater] Current: {current_version} | Latest: {latest_version}")

#         # Already latest
#         if latest_version == current_version:
#             print("[Updater] ✅ Already up to date.")
#             return

#         mandatory = bool(data.get("mandatory", False))

#         # --------------------------------------------------
#         # Prevent popup spam (once per version)
#         # --------------------------------------------------
#         state = _load_update_state()
#         last_prompted = state.get("last_prompted_version")

#         if not mandatory and last_prompted == latest_version:
#             print(f"[Updater] ℹ️ Update {latest_version} already prompted, skipping popup.")
#         else:
#             if not mandatory:
#                 ask_user_to_update(latest_version)

#             state["last_prompted_version"] = latest_version
#             _save_update_state(state)

#         # OS-specific download URL
#         os_type = platform.system()
#         download_url = (
#             data.get("windows_url") if os_type == "Windows"
#             else data.get("mac_url")
#         )

#         if not download_url:
#             show_error("Update Error", "No download URL found in version file.")
#             return

#         # Download installer
#         tmp_file = os.path.join(
#             tempfile.gettempdir(),
#             os.path.basename(download_url)
#         )

#         print(f"[Updater] Downloading from {download_url}")
#         with requests.get(download_url, stream=True, timeout=30) as resp:
#             resp.raise_for_status()
#             with open(tmp_file, "wb") as f:
#                 for chunk in resp.iter_content(chunk_size=8192):
#                     if chunk:
#                         f.write(chunk)

#         print(f"[Updater] Downloaded to: {tmp_file}")

#         # Verify checksum
#         expected = str(data.get("sha256", "")).strip().lower()
#         if expected:
#             actual = sha256(tmp_file)
#             if actual != expected:
#                 os.remove(tmp_file)
#                 show_error(
#                     "Checksum Error",
#                     "Downloaded file failed integrity verification."
#                 )
#                 return

#         # --------------------------------------------------
#         # Launch updater
#         # --------------------------------------------------

#         if os_type == "Windows":
#             updater_path = os.path.join(os.path.dirname(exe_path), "updater.exe")
#             if not os.path.exists(updater_path):
#                 show_error(
#                     "Update Error",
#                     f"Missing updater.exe at:\n{updater_path}"
#                 )
#                 return

#             print(f"[Updater] Launching updater: {updater_path}")
#             subprocess.Popen(
#                 [updater_path, tmp_file, exe_path],
#                 shell=False
#             )

#             time.sleep(2)
#             sys.exit(0)

#         elif os_type == "Darwin":
#             updater_path = os.path.join(os.path.dirname(exe_path), "updater.sh")
#             if not os.path.exists(updater_path):
#                 show_error("Update Error", "Missing updater.sh")
#                 return

#             subprocess.Popen(["bash", updater_path, tmp_file])
#             sys.exit(0)

#     except Exception as e:
#         show_error("Update Failed", str(e))
#         print(f"[Updater] ❌ Update failed: {e}")
