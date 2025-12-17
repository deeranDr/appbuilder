# -------------->  old---> working 
import os
import sys
import time
import psutil
import subprocess

def kill_process_by_name(exe_name):
    """Terminate any running instance of the old app."""
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if exe_name.lower() in proc.info["name"].lower():
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except psutil.TimeoutExpired:
                    proc.kill()
        except Exception:
            pass


def main():
    if len(sys.argv) < 3:
        print("Usage: updater.exe <new_exe_path> <old_exe_path>")
        sys.exit(1)

    new_exe_path = sys.argv[1]   # e.g. C:\Users\Deeran\AppData\Local\Temp\PremediaApp_v1.1.29.exe
    old_exe_path = sys.argv[2]   # e.g. C:\Users\Deeran\AppData\Local\PremediaApp\PremediaApp.exe
    exe_name = os.path.basename(old_exe_path)

    print(f"🔹 Closing old version ({exe_name}) ...")
    kill_process_by_name(exe_name)

    # small delay for OS to release file handles
    time.sleep(1)

    print(f"🚀 Launching new version from: {new_exe_path}")
    try:
        subprocess.Popen([new_exe_path], shell=False)
        print("✅ Update complete – running the new version (no reinstall).")
    except Exception as e:
        print(f"❌ Failed to launch new version: {e}")

    sys.exit(0)


if __name__ == "__main__":
    main()
# ----------------->


# import os
# import sys
# import time
# import shutil
# import psutil
# import subprocess

# def kill_process_by_name(exe_name):
#     for proc in psutil.process_iter(["name"]):
#         try:
#             if proc.info["name"] and exe_name.lower() in proc.info["name"].lower():
#                 proc.terminate()
#                 proc.wait(timeout=5)
#         except Exception:
#             pass


# def main():
#     if len(sys.argv) < 3:
#         sys.exit(1)

#     new_exe_path = sys.argv[1]   # TEMP downloaded exe
#     old_exe_path = sys.argv[2]   # Installed PremediaApp.exe

#     exe_name = os.path.basename(old_exe_path)
#     install_dir = os.path.dirname(old_exe_path)

#     print(f"🔹 Closing old version ({exe_name}) ...")
#     kill_process_by_name(exe_name)
#     time.sleep(1)

#     print("🔹 Replacing installed executable...")
#     shutil.copy2(new_exe_path, old_exe_path)

#     print("🚀 Launching updated app...")
#     subprocess.Popen(
#         [old_exe_path],
#         cwd=install_dir,   # 🔴 CRITICAL
#         shell=False
#     )

#     sys.exit(0)


# if __name__ == "__main__":
#     main()
