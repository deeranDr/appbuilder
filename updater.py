# import os, sys, time, shutil, subprocess, ctypes

# def run_as_admin():
#     """ Relaunch with admin privileges if not already elevated """
#     try:
#         if ctypes.windll.shell32.IsUserAnAdmin():
#             return True
#     except:
#         pass
#     params = " ".join(sys.argv)
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
#     sys.exit(0)

# def main():
#     if len(sys.argv) < 3:
#         sys.exit(1)

#     old_path, new_path = sys.argv[1], sys.argv[2]
#     run_as_admin()  # ensure elevation
#     log_path = os.path.join(os.path.dirname(old_path), "update_log.txt")

#     with open(log_path, "a", encoding="utf-8") as log:
#         log.write(f"\n[{time.ctime()}] Starting update...\n")
#         log.write(f"Old: {old_path}\nNew: {new_path}\n")

#         time.sleep(2)
#         try:
#             shutil.copy2(new_path, old_path)
#             log.write("✅ Copy succeeded.\n")
#         except Exception as e:
#             log.write(f"❌ Update failed: {e}\n")
#             sys.exit(1)

#         try:
#             os.remove(new_path)
#             log.write("Temp file removed.\n")
#         except Exception as e:
#             log.write(f"Failed to remove temp file: {e}\n")

#         subprocess.Popen([old_path])
#         log.write("Relaunched new version.\n")
#         log.write("Done.\n")

# if __name__ == "__main__":
#     main()


import os
import sys
import time
import shutil
import subprocess
import ctypes
import traceback

def run_as_admin():
    """ Relaunch this script with admin rights if not already elevated """
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
    except:
        pass

    params = " ".join([f'"{a}"' for a in sys.argv])
    # 🔹 Relaunch self as admin
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

def main():
    if len(sys.argv) < 3:
        print("Usage: updater.exe <old_path> <new_path>")
        sys.exit(1)

    # 🔹 Correct argument mapping
    old_path = sys.argv[1]  # The currently installed app (e.g. PremediaApp.exe)
    new_path = sys.argv[2]  # The newly downloaded file in temp

    # 🔹 Ensure elevated privileges
    run_as_admin()

    log_path = os.path.join(os.path.dirname(old_path), "update_log.txt")

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n[{time.ctime()}] ======== UPDATE START ========\n")
        log.write(f"Old: {old_path}\nNew: {new_path}\n")

        # 🔹 Step 1: Wait until old app fully exits
        for i in range(30):  # wait up to 30 seconds
            try:
                os.rename(old_path, old_path)  # test if file is free
                log.write("✅ File lock released.\n")
                break
            except PermissionError:
                log.write(f"⏳ Waiting for app to close... ({i+1}/30)\n")
                time.sleep(1)
        else:
            log.write("❌ Timeout: app did not close in 30 seconds.\n")
            sys.exit(1)

        # 🔹 Step 2: Copy new version → old app location
        try:
            if not os.path.exists(new_path):
                log.write(f"❌ New file missing: {new_path}\n")
                sys.exit(1)

            shutil.copy2(new_path, old_path)
            log.write("✅ New version copied successfully.\n")
        except Exception as e:
            log.write(f"❌ Copy failed: {e}\n{traceback.format_exc()}\n")
            sys.exit(1)

        # 🔹 Step 3: Delete temp file safely
        try:
            os.remove(new_path)
            log.write("🧹 Temp file removed.\n")
        except Exception as e:
            log.write(f"⚠️ Could not delete temp file: {e}\n")

        # 🔹 Step 4: Relaunch the updated app
        try:
            subprocess.Popen([old_path], shell=False)
            log.write("🚀 Relaunched new version successfully.\n")
        except Exception as e:
            log.write(f"❌ Relaunch failed: {e}\n{traceback.format_exc()}\n")

        log.write("✅ ======== UPDATE COMPLETE ========\n")


if __name__ == "__main__":
    main()

