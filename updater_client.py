# updater_client.py
# import os
# import sys
# import json
# import time
# import tempfile
# import subprocess
# import hashlib
# import platform
# import requests
# import tkinter as tk
# from tkinter import messagebox

# # 🔹 Hosted version file
# VERSION_URL = "https://vmg-premedia-22112023.s3.ap-southeast-2.amazonaws.com/application/drn/latest_version.json"

# def sha256(path):
#     """Compute lowercase SHA256 checksum."""
#     h = hashlib.sha256()
#     with open(path, "rb") as f:
#         for chunk in iter(lambda: f.read(8192), b""):
#             h.update(chunk)
#     return h.hexdigest().lower()

# def ask_user_to_update(latest):
#     """Ask user if they want to update."""
#     root = tk.Tk()
#     root.withdraw()
#     res = messagebox.askyesno(
#         "Update Available",
#         f"A new version {latest} is available.\nDo you want to update now?"
#     )
#     root.destroy()
#     return res

# def check_for_update(current_version, exe_path):
#     """Check S3 JSON for update and apply if needed."""
#     try:
#         r = requests.get(f"{VERSION_URL}?t={int(time.time())}", timeout=8)
#         data = r.json()
#         latest_version = data.get("version", "").strip()
#         if not latest_version:
#             print("[Updater] ❌ Invalid version JSON.")
#             return

#         print(f"[Updater] Current: {current_version} | Latest: {latest_version}")
#         if latest_version == current_version:
#             print("[Updater] ✅ Already up to date.")
#             return

#         mandatory = bool(data.get("mandatory"))
#         if not mandatory and not ask_user_to_update(latest_version):
#             print("[Updater] Skipped by user.")
#             return

#         os_type = platform.system()
#         download_url = data.get("windows_url") if os_type == "Windows" else data.get("mac_url")
#         if not download_url:
#             messagebox.showerror("Update Error", "No download URL in JSON.")
#             return

#         # 🔹 Download new EXE
#         tmp_file = os.path.join(tempfile.gettempdir(), os.path.basename(download_url))
#         print(f"[Updater] Downloading from {download_url} ...")
#         with requests.get(download_url, stream=True, timeout=30) as resp:
#             resp.raise_for_status()
#             with open(tmp_file, "wb") as f:
#                 for chunk in resp.iter_content(chunk_size=8192):
#                     if chunk:
#                         f.write(chunk)
#         print(f"[Updater] Downloaded to: {tmp_file}")

#         # 🔹 Verify checksum
#         expected = data.get("sha256", "").strip().lower()
#         actual = sha256(tmp_file)
#         if expected and actual != expected:
#             messagebox.showerror("Checksum Error", "Downloaded file failed verification.")
#             os.remove(tmp_file)
#             return

#         # 🔹 Launch updater
#         if os_type == "Windows":
#             updater_path = os.path.join(os.path.dirname(exe_path), "updater.exe")
#             if not os.path.exists(updater_path):
#                 messagebox.showerror("Update Error", f"Missing updater.exe at:\n{updater_path}")
#                 return

#             print(f"[Updater] Launching updater: {updater_path}")
#             subprocess.Popen([updater_path, tmp_file, exe_path], shell=False)

#             # wait a little before exit so file lock clears
#             time.sleep(2)
#             sys.exit(0)

#         elif os_type == "Darwin":
#             updater_path = os.path.join(os.path.dirname(exe_path), "updater.sh")

#             if not os.path.exists(updater_path):
#                 messagebox.showerror("Update Error", "Missing updater.sh")
#                 return

#             subprocess.Popen(["bash", updater_path, tmp_file])
#             sys.exit(0)


#     except Exception as e:
#         print(f"[Updater] ❌ Update failed: {e}")



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

# ============================================================
# CONFIG
# ============================================================

VERSION_URL = "https://vmg-premedia-22112023.s3.ap-southeast-2.amazonaws.com/application/drn/latest_version.json"
UPDATE_CHECK_INTERVAL_SEC = 3 * 60 * 60  # 3 hours

UPDATE_STATE_FILE = os.path.join(
    tempfile.gettempdir(),
    "premedia_update_state.json"
)

# ============================================================
# HELPERS
# ============================================================

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest().lower()


def _load_update_state():
    if not os.path.exists(UPDATE_STATE_FILE):
        return {}
    try:
        with open(UPDATE_STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_update_state(state):
    try:
        with open(UPDATE_STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


def _should_check_update():
    state = _load_update_state()
    last_check = state.get("last_check", 0)

    now = int(time.time())
    if now - last_check >= UPDATE_CHECK_INTERVAL_SEC:
        return True

    remaining = UPDATE_CHECK_INTERVAL_SEC - (now - last_check)
    print(f"[Updater] ⏳ Skipping update check (next in {remaining // 60} min)")
    return False


def _mark_update_checked():
    _save_update_state({"last_check": int(time.time())})


def ask_user_to_update(latest):
    root = tk.Tk()
    root.withdraw()
    res = messagebox.askyesno(
        "Update Available",
        f"A new version {latest} is available.\nDo you want to update now?"
    )
    root.destroy()
    return res

# ============================================================
# MAIN UPDATE LOGIC (3-hour controlled)
# ============================================================

def check_for_update(current_version, exe_path):
    """
    Checks for update at most once every 3 hours.
    If update is found, downloads and launches updater.exe.
    """

    # 🔴 Enforce 3-hour rule HERE
    if not _should_check_update():
        return

    try:
        r = requests.get(f"{VERSION_URL}?t={int(time.time())}", timeout=8)
        r.raise_for_status()
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
        download_url = data.get("windows_url") if os_type == "Windows" else data.get("mac_url")

        if not download_url:
            messagebox.showerror("Update Error", "No download URL in JSON.")
            return

        # ====================================================
        # DOWNLOAD
        # ====================================================

        tmp_file = os.path.join(tempfile.gettempdir(), os.path.basename(download_url))
        print(f"[Updater] Downloading from {download_url} ...")

        with requests.get(download_url, stream=True, timeout=30) as resp:
            resp.raise_for_status()
            with open(tmp_file, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        print(f"[Updater] Downloaded to: {tmp_file}")

        # ====================================================
        # VERIFY
        # ====================================================

        expected = data.get("sha256", "").strip().lower()
        actual = sha256(tmp_file)

        if expected and actual != expected:
            messagebox.showerror("Checksum Error", "Downloaded file failed verification.")
            os.remove(tmp_file)
            return

        # ====================================================
        # APPLY UPDATE
        # ====================================================

        if os_type == "Windows":
            updater_path = os.path.join(os.path.dirname(exe_path), "updater.exe")
            if not os.path.exists(updater_path):
                messagebox.showerror("Update Error", f"Missing updater.exe:\n{updater_path}")
                return

            print(f"[Updater] Launching updater: {updater_path}")
            subprocess.Popen([updater_path, tmp_file, exe_path], shell=False)

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

    finally:
        # ✅ Mark check time whether update happened or not
        _mark_update_checked()
