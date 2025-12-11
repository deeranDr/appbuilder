import os, sys, time, shutil, subprocess, ctypes, traceback

def run_as_admin():
    """ Relaunch with admin privileges if not already elevated """
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
    except:
        pass
    params = " ".join([f'"{a}"' for a in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

def main():
    if len(sys.argv) < 3:
        sys.exit(1)

    old_path, new_path = sys.argv[1], sys.argv[2]
    run_as_admin()  # ensure elevation
    log_path = os.path.join(os.path.dirname(old_path), "update_log.txt")

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n[{time.ctime()}] Starting update...\n")
        log.write(f"Old: {old_path}\nNew: {new_path}\n")

        # 🔹 Wait until the main app has fully closed
        for i in range(20):  # wait up to 20 seconds
            try:
                os.rename(old_path, old_path)  # check if file still locked
                log.write("✅ File lock released.\n")
                break
            except PermissionError:
                log.write("⏳ Waiting for main app to close...\n")
                time.sleep(1)

        # 🔹 Try to copy new EXE
        try:
            shutil.copy2(new_path, old_path)
            log.write("✅ Copy succeeded.\n")
        except Exception as e:
            log.write(f"❌ Update failed: {e}\n{traceback.format_exc()}\n")
            sys.exit(1)

        # 🔹 Remove temp file
        try:
            os.remove(new_path)
            log.write("🧹 Temp file removed.\n")
        except Exception as e:
            log.write(f"⚠️ Failed to remove temp file: {e}\n")

        # 🔹 Relaunch new version
        try:
            subprocess.Popen([old_path])
            log.write("🚀 Relaunched new version.\n")
        except Exception as e:
            log.write(f"❌ Relaunch failed: {e}\n{traceback.format_exc()}\n")

        log.write("✅ Done.\n")

if __name__ == "__main__":
    main()

