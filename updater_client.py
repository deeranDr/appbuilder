# updater_client.py
import os, sys, json, tempfile, subprocess, hashlib, platform, requests, tkinter as tk
from tkinter import messagebox

# CloudFront base URL
VERSION_URL = "https://vmg-premedia-22112023.s3.ap-southeast-2.amazonaws.com/application/drn/latest_version.json"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def ask_user_to_update(latest):
    root = tk.Tk()
    root.withdraw()
    res = messagebox.askyesno(
        "Update Available",
        f"A new version {latest} is available.\nDo you want to update now?"
    )
    root.destroy()
    return res

def check_for_update(current_version, exe_path):
    try:
        r = requests.get(VERSION_URL, timeout=5)
        data = r.json()
        latest = data["version"]

        if latest != current_version:
            if ask_user_to_update(latest):
                os_type = platform.system()
                if os_type == "Windows":
                    url = data.get("windows_url")
                elif os_type == "Darwin":
                    url = data.get("mac_url")
                else:
                    print("Auto-update not supported on this OS.")
                    return

                tmp = os.path.join(tempfile.gettempdir(), os.path.basename(url))
                print(f"Downloading update: {url}")
                with open(tmp, "wb") as f:
                    f.write(requests.get(url).content)

                if sha256(tmp) == data.get("sha256"):
                    if os_type == "Windows":
                        subprocess.Popen(["updater.exe", exe_path, tmp])
                        sys.exit(0)
                    elif os_type == "Darwin":
                        subprocess.Popen(["open", tmp])  # open dmg/pkg
                        sys.exit(0)
                else:
                    messagebox.showerror("Update Error", "Checksum mismatch.")
        else:
            print(" Already up to date.")
    except Exception as e:
        print("Update check failed:", e)
