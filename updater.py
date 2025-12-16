# # updater.py
# import os
# import sys
# import time
# import shutil
# import subprocess
# import psutil
# import traceback
# import ctypes

# MOVEFILE_DELAY_UNTIL_REBOOT = 0x00000004
# MoveFileExW = ctypes.windll.kernel32.MoveFileExW

# def kill_process(exe_name):
#     """Kill running process by name."""
#     for proc in psutil.process_iter(["name", "pid"]):
#         try:
#             if proc.info["name"] and exe_name.lower() in proc.info["name"].lower():
#                 proc.terminate()
#                 try:
#                     proc.wait(timeout=5)
#                 except psutil.TimeoutExpired:
#                     proc.kill()
#         except Exception:
#             pass

# def wait_for_unlock(path, timeout=15):
#     for _ in range(timeout):
#         try:
#             os.rename(path, path)
#             return True
#         except PermissionError:
#             time.sleep(1)
#     return False

# def replace_file_safely(src, dst, log):
#     """Copy new file over old one. If locked, schedule for next reboot."""
#     try:
#         shutil.copy2(src, dst)
#         log.write("✅ File replaced immediately.\n")
#         return True
#     except Exception as e:
#         log.write(f"⚠️ Replace failed: {e}\n")
#         tmp = dst + ".new"
#         shutil.copy2(src, tmp)
#         res = MoveFileExW(tmp, dst, MOVEFILE_DELAY_UNTIL_REBOOT)
#         if res:
#             log.write("🔁 Scheduled replace at reboot.\n")
#             return True
#         else:
#             log.write("❌ Could not schedule replace.\n")
#             return False

# def main():
#     if len(sys.argv) < 3:
#         sys.exit(1)

#     new_path, old_path = sys.argv[1], sys.argv[2]
#     exe_name = os.path.basename(old_path)
#     log_path = os.path.join(os.path.dirname(old_path), "update_log.txt")

#     with open(log_path, "a", encoding="utf-8") as log:
#         log.write(f"\n[{time.ctime()}] ==== UPDATE START ====\n")
#         log.write(f"Old: {old_path}\nNew: {new_path}\n")

#         kill_process(exe_name)
#         wait_for_unlock(old_path)

#         if replace_file_safely(new_path, old_path, log):
#             try:
#                 os.remove(new_path)
#             except OSError:
#                 pass
#             try:
#                 subprocess.Popen([old_path])
#                 log.write("🚀 Relaunched updated app.\n")
#             except Exception as e:
#                 log.write(f"❌ Relaunch failed: {e}\n{traceback.format_exc()}\n")

#         log.write("==== UPDATE COMPLETE ====\n")

# if __name__ == "__main__":
#     main()
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
