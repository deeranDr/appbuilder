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

#     # --- Fix duplicate self path added by ShellExecuteW ---
#     if len(sys.argv) >= 4 and sys.argv[1].endswith("updater.exe"):
#         sys.argv.pop(1)        

#     # Correct argument mapping
#     new_path = sys.argv[1]  # The new downloaded file (from temp)
#     old_path = sys.argv[2]  # The currently installed app (PremediaApp.exe)

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
#     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
#     sys.exit(0)


# def wait_for_file_release(path, log, timeout=30):
#     """ Waits until the file is not locked by any process """
#     for i in range(timeout):
#         # Check write permission
#         if os.access(path, os.W_OK):
#             try:
#                 os.rename(path, path)  # Windows-like lock test
#                 log.write("✅ File lock released.\n")
#                 return True
#             except PermissionError:
#                 pass

#         log.write(f"⏳ Waiting for file to unlock... ({i+1}/{timeout})\n")
#         time.sleep(1)

#     return False


# def main():
#     if len(sys.argv) < 3:
#         print("Usage: updater.exe <new_path> <old_path>")
#         sys.exit(1)

#     # Remove duplicated self-inserted path when elevated
#     if len(sys.argv) >= 4 and "updater" in sys.argv[1].lower():
#         sys.argv.pop(1)

#     new_path = sys.argv[1]
#     old_path = sys.argv[2]

#     # Run as admin if needed
#     run_as_admin()

#     log_path = os.path.join(os.path.dirname(old_path), "update_log.txt")

#     with open(log_path, "a", encoding="utf-8") as log:
#         log.write(f"\n[{time.ctime()}] ======== UPDATE START ========\n")
#         log.write(f"Old: {old_path}\nNew: {new_path}\n")

#         # 1️⃣ Wait for the old EXE to be free
#         if not wait_for_file_release(old_path, log):
#             log.write("❌ Timeout: app never released the file.\n")
#             sys.exit(1)

#         # 2️⃣ Delete old exe first (prevents PermissionError)
#         try:
#             log.write("🗑 Deleting old version...\n")
#             os.remove(old_path)
#         except Exception as e:
#             log.write(f"❌ Failed to delete old file: {e}\n{traceback.format_exc()}\n")
#             sys.exit(1)

#         # 3️⃣ Copy new exe into place
#         try:
#             if not os.path.exists(new_path):
#                 log.write(f"❌ New file missing: {new_path}\n")
#                 sys.exit(1)

#             log.write("📄 Copying new version...\n")
#             shutil.copy2(new_path, old_path)
#             log.write("✅ New version copied successfully.\n")
#         except Exception as e:
#             log.write(f"❌ Copy failed: {e}\n{traceback.format_exc()}\n")
#             sys.exit(1)

#         # 4️⃣ Delete temp file
#         try:
#             os.remove(new_path)
#             log.write("🧹 Temp file removed.\n")
#         except Exception as e:
#             log.write(f"⚠️ Could not delete temp file: {e}\n")

#         # 5️⃣ Relaunch updated EXE
#         try:
#             subprocess.Popen([old_path], shell=False)
#             log.write("🚀 Relaunched updated version.\n")
#         except Exception as e:
#             log.write(f"❌ Relaunch failed: {e}\n{traceback.format_exc()}\n")

#         log.write("✅ ======== UPDATE COMPLETE ========\n")


# if __name__ == "__main__":
#     main()
# ------------------------------------------------------>


import os
import sys
import time
import shutil
import subprocess
import ctypes
import traceback


def run_as_admin():
    """Relaunch this script with admin rights if not already elevated."""
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
    except Exception:
        # If check fails, try to elevate anyway
        pass

    params = " ".join([f'"{a}"' for a in sys.argv])
    rc = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )
    # If elevation launched successfully, exit current (non‑admin) process
    if rc > 32:
        sys.exit(0)
    else:
        raise RuntimeError(f"UAC elevation failed with code {rc}")


def wait_for_file_release(path, log, timeout=30):
    """Waits until the file is not locked by any process (best-effort)."""
    for i in range(timeout):
        if os.access(path, os.W_OK):
            try:
                # simple lock test
                os.rename(path, path)
                log.write("✅ File lock released.\n")
                return True
            except PermissionError:
                pass

        log.write(f"⏳ Waiting for file to unlock... ({i + 1}/{timeout})\n")
        time.sleep(1)

    return False


def main():
    if len(sys.argv) < 3:
        print("Usage: updater.exe <new_path> <old_path>")
        sys.exit(1)

    # Remove duplicated self-inserted path when elevated
    if len(sys.argv) >= 4 and "updater" in sys.argv[1].lower():
        sys.argv.pop(1)

    new_path = sys.argv[1]
    old_path = sys.argv[2]

    # Ensure this instance is elevated
    if not run_as_admin():
        sys.exit(1)

    log_path = os.path.join(os.path.dirname(old_path), "update_log.txt")

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n[{time.ctime()}] ======== UPDATE START ========\n")
        log.write(f"Old: {old_path}\nNew: {new_path}\n")

        # 1️⃣ Wait for the old EXE to be free (best-effort)
        if not wait_for_file_release(old_path, log):
            log.write("❌ Timeout: app never released the file.\n")
            sys.exit(1)

        # 2️⃣ Safely rotate old exe instead of deleting
        backup = old_path + ".old"
        try:
            # Try to cleanup previous backup if it exists
            if os.path.exists(backup):
                try:
                    os.remove(backup)
                    log.write("🧹 Previous backup removed.\n")
                except PermissionError as e:
                    log.write(f"⚠️ Could not delete previous backup: {e}\n")

            log.write("♻️ Renaming old exe to backup...\n")
            os.rename(old_path, backup)
            log.write("✅ Old exe renamed to backup.\n")
        except Exception as e:
            log.write(f"❌ Failed to rotate old exe: {e}\n{traceback.format_exc()}\n")
            sys.exit(1)

        # 3️⃣ Copy new exe into place
        try:
            if not os.path.exists(new_path):
                log.write(f"❌ New file missing: {new_path}\n")
                sys.exit(1)

            log.write("📄 Copying new version...\n")
            shutil.copy2(new_path, old_path)
            log.write("✅ New version copied successfully.\n")
        except Exception as e:
            log.write(f"❌ Copy failed: {e}\n{traceback.format_exc()}\n")
            # Optional: try to restore backup on failure
            try:
                if os.path.exists(backup):
                    shutil.copy2(backup, old_path)
                    log.write("↩️ Restored old exe from backup.\n")
            except Exception as e2:
                log.write(f"⚠️ Failed to restore old exe: {e2}\n")
            sys.exit(1)

        # 4️⃣ Delete temp file
        try:
            os.remove(new_path)
            log.write("🧹 Temp file removed.\n")
        except Exception as e:
            log.write(f"⚠️ Could not delete temp file: {e}\n")

        # 5️⃣ Relaunch updated EXE
        try:
            subprocess.Popen([old_path], shell=False)
            log.write("🚀 Relaunched updated version.\n")
        except Exception as e:
            log.write(f"❌ Relaunch failed: {e}\n{traceback.format_exc()}\n")

        log.write("✅ ======== UPDATE COMPLETE ========\n")


if __name__ == "__main__":
    main()
