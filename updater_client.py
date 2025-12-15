# # updater_client.py
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

# # 🔹 S3 location of version file
# VERSION_URL = "https://vmg-premedia-22112023.s3.ap-southeast-2.amazonaws.com/application/drn/latest_version.json"


# # ====================================================
# #  Utility functions
# # ====================================================

# # def sha256(path):
# #     """Compute SHA256 checksum of a file."""
# #     h = hashlib.sha256()
# #     with open(path, "rb") as f:
# #         for chunk in iter(lambda: f.read(8192), b""):
# #             h.update(chunk)
# #     return h.hexdigest().upper()

# def sha256(path):
#     """Compute SHA256 checksum of a file."""
#     h = hashlib.sha256()
#     with open(path, "rb") as f:
#         for chunk in iter(lambda: f.read(8192), b""):
#             h.update(chunk)
#     # 🔹 Always return lowercase to match S3 JSON and prevent case mismatch
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


# # ====================================================
# #  Main update logic
# # ====================================================

# def check_for_update(current_version, exe_path):
#     """
#     Check remote JSON for new version, download and apply update if needed.
#     """
#     try:
#         # 🔹 Step 1: Fetch latest version JSON (with cache-busting)
#         response = requests.get(f"{VERSION_URL}?t={int(time.time())}", timeout=8)
#         data = response.json()
#         latest_version = data.get("version", "").strip()

#         if not latest_version:
#             print("[Updater] ❌ No version info in JSON.")
#             return

#         print(f"[Updater] Current: {current_version} | Latest: {latest_version}")

#         # 🔹 Step 2: Compare versions
#         if latest_version == current_version:
#             print("[Updater] ✅ Already up to date.")
#             return

#         # 🔹 Step 3: Ask user for confirmation (unless mandatory)
#         mandatory = bool(data.get("mandatory"))
#         if not mandatory:
#             if not ask_user_to_update(latest_version):
#                 print("[Updater] Skipped by user.")
#                 return
#         else:
#             print("[Updater] Mandatory update enforced.")

#         # 🔹 Step 4: Select correct OS download URL
#         os_type = platform.system()
#         if os_type == "Windows":
#             download_url = data.get("windows_url")
#         elif os_type == "Darwin":
#             download_url = data.get("mac_url")
#         else:
#             messagebox.showinfo("Unsupported OS", "Auto-update is not supported on this OS.")
#             return

#         if not download_url:
#             messagebox.showerror("Update Error", "Download URL missing in JSON.")
#             return

#         # 🔹 Step 5: Download new build
#         print(f"[Updater] Downloading from: {download_url}")
#         tmp_file = os.path.join(tempfile.gettempdir(), os.path.basename(download_url))

#         with requests.get(download_url, stream=True, timeout=30) as r:
#             r.raise_for_status()
#             with open(tmp_file, "wb") as f:
#                 for chunk in r.iter_content(chunk_size=8192):
#                     if chunk:
#                         f.write(chunk)

#         print(f"[Updater] Downloaded to temp: {tmp_file}")

#         # 🔹 Step 6: Verify SHA256 checksum (case-insensitive)
#         expected_hash = data.get("sha256", "").strip().lower()
#         actual_hash = sha256(tmp_file).strip().lower()

#         print(f"[Updater] Expected SHA256: {expected_hash}")
#         print(f"[Updater] Actual SHA256:   {actual_hash}")

#         if expected_hash and actual_hash != expected_hash:
#             print(f"[Updater] ❌ Mismatch detected (len expected={len(expected_hash)}, len actual={len(actual_hash)})")
#             messagebox.showerror(
#                 "Update Error",
#                 f"Checksum mismatch detected.\n\n"
#                 f"Expected: {expected_hash}\n"
#                 f"Actual:   {actual_hash}\n\n"
#                 f"The downloaded file may be corrupted. Please try again."
#             )
#             try:
#                 os.remove(tmp_file)
#             except OSError:
#                 pass
#             return
#         else:
#             print("[Updater] ✅ SHA256 verified successfully.")


#         # 🔹 Step 7: Launch updater
#         if os_type == "Windows":
#             updater_path = os.path.join(os.path.dirname(exe_path), "updater.exe")

#             if not os.path.exists(updater_path):
#                 messagebox.showerror("Update Error", f"Missing updater.exe at:\n{updater_path}")
#                 return

#             print(f"[Updater] Launching updater: {updater_path}")
#             subprocess.Popen([updater_path, tmp_file, exe_path])
#             sys.exit(0)


#         elif os_type == "Darwin":
#             updater_path = os.path.join(os.path.dirname(exe_path), "sayhi.sh")

#             if not os.path.exists(updater_path):

#                 messagebox.showerror("Update Error", f"Missing sayhi.sh at:\n{updater_path}")
#                 return

#             print(f"[Updater] Launching updater: {updater_path}")
#             subprocess.Popen(["bash", updater_path, tmp_file])
#             sys.exit(0)



#     except requests.exceptions.RequestException as e:
#         print(f"[Updater] Network error: {e}")
#     except json.JSONDecodeError as e:
#         print(f"[Updater] Invalid JSON file: {e}")
#     except Exception as e:
#         print(f"[Updater] Unexpected error: {e}")


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
        download_url = data.get("windows_url") if os_type == "Windows" else data.get("mac_url")
        if not download_url:
            messagebox.showerror("Update Error", "No download URL in JSON.")
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
            messagebox.showinfo("Info", "Use macOS .sh logic here if needed.")

    except Exception as e:
        print(f"[Updater] ❌ Update failed: {e}")
