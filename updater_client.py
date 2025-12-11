# # updater_client.py
# import os, sys, json, tempfile, subprocess, hashlib, platform, requests, tkinter as tk
# from tkinter import messagebox

# # CloudFront base URL
# VERSION_URL = "https://vmg-premedia-22112023.s3.ap-southeast-2.amazonaws.com/application/drn/latest_version.json"


# def sha256(path):
#     h = hashlib.sha256()
#     with open(path, "rb") as f:
#         for chunk in iter(lambda: f.read(8192), b""):
#             h.update(chunk)
#     return h.hexdigest()

# def ask_user_to_update(latest):
#     root = tk.Tk()
#     root.withdraw()
#     res = messagebox.askyesno(
#         "Update Available",
#         f"A new version {latest} is available.\nDo you want to update now?"
#     )
#     root.destroy()
#     return res

# def check_for_update(current_version, exe_path):
#     try:
#         r = requests.get(VERSION_URL, timeout=5)
#         data = r.json()
#         latest = data["version"]

#         if latest != current_version:
#             if ask_user_to_update(latest):
#                 os_type = platform.system()
#                 if os_type == "Windows":
#                     url = data.get("windows_url")
#                 elif os_type == "Darwin":
#                     url = data.get("mac_url")
#                 else:
#                     print("Auto-update not supported on this OS.")
#                     return

#                 tmp = os.path.join(tempfile.gettempdir(), os.path.basename(url))
#                 print(f"Downloading update: {url}")
#                 with open(tmp, "wb") as f:
#                     f.write(requests.get(url).content)
#                 print(f"Downloaded to: {tmp}")
#                 print(data.get("sha256", ")"))
#                 if sha256(tmp).strip().upper() == data.get("sha256", "").strip().upper():
#                     print("Update downloaded successfully.")
#                     if os_type == "Windows":
#                         subprocess.Popen(["updater.exe", exe_path, tmp])
#                         sys.exit(0)
#                     elif os_type == "Darwin":
#                         subprocess.Popen(["open", tmp])  # open dmg/pkg
#                         sys.exit(0)
#                 else:
#                     messagebox.showerror("Update Error", "Checksum mismatch.")
#         else:
#             print(" Already up to date.")
#     except Exception as e:
#         print("Update check failed:", e)

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

# 🔹 S3 location of version file
VERSION_URL = "https://vmg-premedia-22112023.s3.ap-southeast-2.amazonaws.com/application/drn/latest_version.json"


# ====================================================
#  Utility functions
# ====================================================

def sha256(path):
    """Compute SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest().upper()


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


# ====================================================
#  Main update logic
# ====================================================

def check_for_update(current_version, exe_path):
    """
    Check remote JSON for new version, download and apply update if needed.
    """
    try:
        # 🔹 Step 1: Fetch latest version JSON (with cache-busting)
        response = requests.get(f"{VERSION_URL}?t={int(time.time())}", timeout=8)
        data = response.json()
        latest_version = data.get("version", "").strip()

        if not latest_version:
            print("[Updater] ❌ No version info in JSON.")
            return

        print(f"[Updater] Current: {current_version} | Latest: {latest_version}")

        # 🔹 Step 2: Compare versions
        if latest_version == current_version:
            print("[Updater] ✅ Already up to date.")
            return

        # 🔹 Step 3: Ask user for confirmation (unless mandatory)
        mandatory = bool(data.get("mandatory"))
        if not mandatory:
            if not ask_user_to_update(latest_version):
                print("[Updater] Skipped by user.")
                return
        else:
            print("[Updater] Mandatory update enforced.")

        # 🔹 Step 4: Select correct OS download URL
        os_type = platform.system()
        if os_type == "Windows":
            download_url = data.get("windows_url")
        elif os_type == "Darwin":
            download_url = data.get("mac_url")
        else:
            messagebox.showinfo("Unsupported OS", "Auto-update is not supported on this OS.")
            return

        if not download_url:
            messagebox.showerror("Update Error", "Download URL missing in JSON.")
            return

        # 🔹 Step 5: Download new build
        print(f"[Updater] Downloading from: {download_url}")
        tmp_file = os.path.join(tempfile.gettempdir(), os.path.basename(download_url))

        with requests.get(download_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(tmp_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        print(f"[Updater] Downloaded to temp: {tmp_file}")

        # 🔹 Step 6: Verify SHA256 checksum
        expected_hash = data.get("sha256", "").strip().upper()
        actual_hash = sha256(tmp_file)

        print(f"[Updater] Expected SHA256: {expected_hash}")
        print(f"[Updater] Actual SHA256:   {actual_hash}")

        if expected_hash and actual_hash != expected_hash:
            messagebox.showerror("Update Error", "Checksum mismatch. Download may be corrupted.")
            os.remove(tmp_file)
            return

        # 🔹 Step 7: Launch updater
        if os_type == "Windows":
            updater_path = os.path.join(os.path.dirname(exe_path), "updater.exe")

            if not os.path.exists(updater_path):
                messagebox.showerror("Update Error", f"Missing updater.exe at:\n{updater_path}")
                return

            print(f"[Updater] Launching updater: {updater_path}")
            subprocess.Popen([updater_path, tmp_file, exe_path])
            sys.exit(0)

        elif os_type == "Darwin":
            subprocess.Popen(["open", tmp_file])  # open DMG/pkg
            sys.exit(0)

    except requests.exceptions.RequestException as e:
        print(f"[Updater] Network error: {e}")
    except json.JSONDecodeError as e:
        print(f"[Updater] Invalid JSON file: {e}")
    except Exception as e:
        print(f"[Updater] Unexpected error: {e}")
