import os
import sys
import time
import shutil
import subprocess
import ctypes
import traceback
import psutil


def run_as_admin():
    """Relaunch this script with admin rights if not already elevated."""
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
    except Exception:
        pass  # fallback to elevation anyway

    params = " ".join([f'"{a}"' for a in sys.argv])
    rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    if rc > 32:
        sys.exit(0)
    else:
        raise RuntimeError(f"UAC elevation failed with code {rc}")


def kill_process_by_name(exe_name, log):
    """Force-kill all processes matching the given exe name."""
    log.write(f"💀 Checking for running processes: {exe_name}\n")
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] and exe_name.lower() in proc.info["name"].lower():
                log.write(f"⚠️ Terminating {proc.info['name']} (PID {proc.info['pid']})...\n")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                    log.write("✅ Process terminated gracefully.\n")
                except psutil.TimeoutExpired:
                    log.write("⏳ Graceful timeout. Forcing kill...\n")
                    proc.kill()
                    log.write("✅ Process force-killed.\n")
        except Exception as e:
            log.write(f"⚠️ Could not terminate a process: {e}\n")


def wait_for_file_release(path, log, timeout=30):
    """Wait until file becomes writable."""
    for i in range(timeout):
        if os.access(path, os.W_OK):
            try:
                os.rename(path, path)
                log.write("✅ File lock released.\n")
                return True
            except PermissionError:
                pass
        log.write(f"⏳ Waiting for file unlock... ({i + 1}/{timeout})\n")
        time.sleep(1)
    return False


def main():
    if len(sys.argv) < 3:
        print("Usage: updater.exe <new_path> <old_path>")
        sys.exit(1)

    if len(sys.argv) >= 4 and "updater" in sys.argv[1].lower():
        sys.argv.pop(1)

    new_path = sys.argv[1]
    old_path = sys.argv[2]

    # ensure elevated
    if not run_as_admin():
        sys.exit(1)

    log_path = os.path.join(os.path.dirname(old_path), "update_log.txt")
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n[{time.ctime()}] ======== UPDATE START ========\n")
        log.write(f"Old: {old_path}\nNew: {new_path}\n")

        # 🔹 1. Kill the running app first
        exe_name = os.path.basename(old_path)
        kill_process_by_name(exe_name, log)

        # 🔹 2. Wait for release
        if not wait_for_file_release(old_path, log):
            log.write("❌ Timeout waiting for file release.\n")
            sys.exit(1)

        # 🔹 3. Backup old EXE
        backup = old_path + ".old"
        try:
            if os.path.exists(backup):
                os.remove(backup)
                log.write("🧹 Old backup removed.\n")
            os.rename(old_path, backup)
            log.write("✅ Old exe renamed to backup.\n")
        except Exception as e:
            log.write(f"❌ Failed to backup old exe: {e}\n{traceback.format_exc()}\n")
            sys.exit(1)

        # 🔹 4. Copy new version
        try:
            shutil.copy2(new_path, old_path)
            log.write("✅ New version copied.\n")
        except Exception as e:
            log.write(f"❌ Copy failed: {e}\n{traceback.format_exc()}\n")
            if os.path.exists(backup):
                shutil.copy2(backup, old_path)
                log.write("↩️ Restored old exe from backup.\n")
            sys.exit(1)

        # 🔹 5. Clean temp
        try:
            os.remove(new_path)
            log.write("🧹 Temp file removed.\n")
        except Exception as e:
            log.write(f"⚠️ Could not delete temp file: {e}\n")

        # 🔹 6. Relaunch app
        try:
            subprocess.Popen([old_path], shell=False)
            log.write("🚀 Relaunched updated version.\n")
        except Exception as e:
            log.write(f"❌ Relaunch failed: {e}\n{traceback.format_exc()}\n")

        log.write("✅ ======== UPDATE COMPLETE ========\n")


if __name__ == "__main__":
    main()
