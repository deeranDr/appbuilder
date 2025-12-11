# import os
# import sys
# import time
# import shutil
# import subprocess
# import ctypes
# import traceback

# def run_as_admin():
#     """ Relaunch this script with admin rights if not already elevated """
#     try:
#         if ctypes.windll.shell32.IsUserAnAdmin():
#             return True
#     except:
#         pass

#     params = " ".join([f'"{a}"' for a in sys.argv])
#     # 🔹 Relaunch self as admin
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
#     sys.exit(0)

# def main():
#     if len(sys.argv) < 3:
#         print("Usage: updater.exe <old_path> <new_path>")
#         sys.exit(1)

#     # 🔹 Correct argument mapping
#     old_path = sys.argv[1]  # The currently installed app (e.g. PremediaApp.exe)
#     new_path = sys.argv[2]  # The newly downloaded file in temp

#     # 🔹 Ensure elevated privileges
#     run_as_admin()

#     log_path = os.path.join(os.path.dirname(old_path), "update_log.txt")

#     with open(log_path, "a", encoding="utf-8") as log:
#         log.write(f"\n[{time.ctime()}] ======== UPDATE START ========\n")
#         log.write(f"Old: {old_path}\nNew: {new_path}\n")

#         # 🔹 Step 1: Wait until old app fully exits
#         for i in range(30):  # wait up to 30 seconds
#             try:
#                 os.rename(old_path, old_path)  # test if file is free
#                 log.write("✅ File lock released.\n")
#                 break
#             except PermissionError:
#                 log.write(f"⏳ Waiting for app to close... ({i+1}/30)\n")
#                 time.sleep(1)
#         else:
#             log.write("❌ Timeout: app did not close in 30 seconds.\n")
#             sys.exit(1)

#         # 🔹 Step 2: Copy new version → old app location
#         try:
#             if not os.path.exists(new_path):
#                 log.write(f"❌ New file missing: {new_path}\n")
#                 sys.exit(1)

#             shutil.copy2(new_path, old_path)
#             log.write("✅ New version copied successfully.\n")
#         except Exception as e:
#             log.write(f"❌ Copy failed: {e}\n{traceback.format_exc()}\n")
#             sys.exit(1)

#         # 🔹 Step 3: Delete temp file safely
#         try:
#             os.remove(new_path)
#             log.write("🧹 Temp file removed.\n")
#         except Exception as e:
#             log.write(f"⚠️ Could not delete temp file: {e}\n")

#         # 🔹 Step 4: Relaunch the updated app
#         try:
#             subprocess.Popen([old_path], shell=False)
#             log.write("🚀 Relaunched new version successfully.\n")
#         except Exception as e:
#             log.write(f"❌ Relaunch failed: {e}\n{traceback.format_exc()}\n")

#         log.write("✅ ======== UPDATE COMPLETE ========\n")


# if __name__ == "__main__":
#     main()

# updater.py
# updater.py
import os
import sys
import time
import shutil
import subprocess
import ctypes
import traceback
from pathlib import Path


def run_as_admin():
    """Relaunch the script with administrator privileges if not already elevated."""
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
    except Exception:
        pass

    # Not admin → ask for elevation
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )
    sys.exit(0)


def safe_replace(src: str, dst: str, log) -> bool:
    """
    Replace dst with src even if dst is the currently running updater.exe.
    Uses the classic rename-to-.old trick + retry loop.
    """
    dst_path = Path(dst)
    backup = f"{dst}.old"

    # Remove any previous backup
    try:
        if os.path.exists(backup):
            os.remove(backup)
    except Exception:
        pass

    # Step 1: Rename current file to .old → instantly releases Windows lock
    if os.path.exists(dst):
        for _ in range(10):
            try:
                os.rename(dst, backup)
                log.write(f"   Renamed {dst_path.name} → {dst_path.name}.old\n")
                break
            except PermissionError:
                time.sleep(0.5)
        else:
            log.write(f"   Could not rename {dst_path.name} to .old (still locked)\n")

    # Step 2: Copy new file with retries (AV loves to scan right now)
    for attempt in range(20):
        try:
            shutil.copy2(src, dst)
            try:
                os.chmod(dst, 0o755)
            except Exception:
                pass
            log.write(f"   Copied → {dst_path.name}\n")
            return True
        except PermissionError:
            log.write(f"   Attempt {attempt + 1}/20: file still locked, retrying...\n")
            time.sleep(0.4)
        except Exception as e:
            log.write(f"   Copy error: {e}\n")
            break

    log.write("Failed to replace file after all retries.\n")
    return False


def main():
    if len(sys.argv) < 3:
        print("Usage: updater.exe <new_temp_file> <target_exe>")
        sys.exit(1)

    new_file = sys.argv[1]      # downloaded file in temp folder
    target_exe = sys.argv[2]    # PremediaApp.exe OR updater.exe itself

    # Force admin rights (required when installed in Program Files)
    run_as_admin()

    app_dir = os.path.dirname(target_exe)
    log_path = os.path.join(app_dir, "update_log.txt")

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n[{time.ctime()}] ======== UPDATE START ========\n")
        log.write(f"Source : {new_file}\n")
        log.write(f"Target : {target_exe}\n")

        # Only wait for the main app to close – updater.exe is already running (this process)
        if os.path.basename(target_exe).lower() != "updater.exe":
            for i in range(30):
                try:
                    os.rename(target_exe, target_exe)  # no-op rename = lock test
                    log.write("File lock released.\n")
                    break
                except PermissionError:
                    log.write(f"   Waiting for app to exit... ({i + 1}/30)\n")
                    time.sleep(1)
            else:
                log.write("Timeout: main app did not close in 30 seconds.\n")
                sys.exit(1)

        # Replace the file (works for both PremediaApp.exe and updater.exe)
        if not safe_replace(new_file, target_exe, log):
            sys.exit(1)

        # Clean up the temporary